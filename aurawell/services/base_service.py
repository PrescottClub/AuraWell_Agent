"""
Base Service Class for AuraWell

Provides common functionality for all service classes including
async patterns, error handling, and logging.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceResult(Generic[T]):
    """Standard service result wrapper"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, data: T, metadata: Optional[Dict[str, Any]] = None) -> 'ServiceResult[T]':
        """Create a successful result"""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error_result(cls, error: str, error_code: Optional[str] = None, 
                    metadata: Optional[Dict[str, Any]] = None) -> 'ServiceResult[T]':
        """Create an error result"""
        return cls(success=False, error=error, error_code=error_code, metadata=metadata)


@dataclass
class HealthCheck:
    """Health check result"""
    service_name: str
    status: ServiceStatus
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class BaseService(ABC):
    """
    Base service class with common functionality
    
    Provides:
    - Async/await patterns
    - Error handling and logging
    - Health checks
    - Rate limiting
    - Retry logic
    """
    
    def __init__(self, service_name: str) -> None:
        """
        Initialize base service
        
        Args:
            service_name: Name of the service for logging and monitoring
        """
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self._is_initialized = False
        self._health_status = ServiceStatus.UNKNOWN
        
        self.logger.info(f"Service {service_name} created")
    
    async def initialize(self) -> bool:
        """
        Initialize the service
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            await self._initialize_service()
            self._is_initialized = True
            self._health_status = ServiceStatus.HEALTHY
            self.logger.info(f"Service {self.service_name} initialized successfully")
            return True
        except Exception as e:
            self._health_status = ServiceStatus.UNHEALTHY
            self.logger.error(f"Failed to initialize service {self.service_name}: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            await self._shutdown_service()
            self._is_initialized = False
            self._health_status = ServiceStatus.UNKNOWN
            self.logger.info(f"Service {self.service_name} shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during service {self.service_name} shutdown: {e}")
    
    async def health_check(self) -> HealthCheck:
        """
        Perform health check
        
        Returns:
            HealthCheck result
        """
        try:
            if not self._is_initialized:
                return HealthCheck(
                    service_name=self.service_name,
                    status=ServiceStatus.UNHEALTHY,
                    message="Service not initialized",
                    timestamp=datetime.now(timezone.utc)
                )
            
            # Perform service-specific health check
            health_details = await self._perform_health_check()
            
            return HealthCheck(
                service_name=self.service_name,
                status=self._health_status,
                message="Service is healthy",
                timestamp=datetime.now(timezone.utc),
                details=health_details
            )
            
        except Exception as e:
            self._health_status = ServiceStatus.UNHEALTHY
            return HealthCheck(
                service_name=self.service_name,
                status=ServiceStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now(timezone.utc)
            )
    
    async def execute_with_retry(
        self,
        operation: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0
    ) -> ServiceResult[Any]:
        """
        Execute operation with retry logic
        
        Args:
            operation: Async operation to execute
            max_retries: Maximum number of retries
            delay: Initial delay between retries (seconds)
            backoff_factor: Multiplier for delay on each retry
            
        Returns:
            ServiceResult with operation result
        """
        last_error = None
        current_delay = delay
        
        for attempt in range(max_retries + 1):
            try:
                result = await operation()
                return ServiceResult.success_result(result)
                
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                
                if attempt < max_retries:
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
        
        return ServiceResult.error_result(
            error=f"Operation failed after {max_retries + 1} attempts: {str(last_error)}",
            error_code="RETRY_EXHAUSTED"
        )
    
    async def execute_with_timeout(
        self,
        operation: Callable,
        timeout_seconds: float = 30.0
    ) -> ServiceResult[Any]:
        """
        Execute operation with timeout
        
        Args:
            operation: Async operation to execute
            timeout_seconds: Timeout in seconds
            
        Returns:
            ServiceResult with operation result
        """
        try:
            result = await asyncio.wait_for(operation(), timeout=timeout_seconds)
            return ServiceResult.success_result(result)
            
        except asyncio.TimeoutError:
            return ServiceResult.error_result(
                error=f"Operation timed out after {timeout_seconds} seconds",
                error_code="TIMEOUT"
            )
        except Exception as e:
            return ServiceResult.error_result(
                error=str(e),
                error_code="EXECUTION_ERROR"
            )
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._is_initialized
    
    def get_status(self) -> ServiceStatus:
        """Get current service status"""
        return self._health_status
    
    @abstractmethod
    async def _initialize_service(self) -> None:
        """Service-specific initialization logic"""
        pass
    
    @abstractmethod
    async def _shutdown_service(self) -> None:
        """Service-specific shutdown logic"""
        pass
    
    @abstractmethod
    async def _perform_health_check(self) -> Optional[Dict[str, Any]]:
        """Service-specific health check logic"""
        pass


class ServiceManager:
    """
    Manager for coordinating multiple services
    """
    
    def __init__(self) -> None:
        """Initialize service manager"""
        self.services: Dict[str, BaseService] = {}
        self.logger = logging.getLogger(f"{__name__}.ServiceManager")
    
    def register_service(self, service: BaseService) -> None:
        """
        Register a service
        
        Args:
            service: Service instance to register
        """
        self.services[service.service_name] = service
        self.logger.info(f"Registered service: {service.service_name}")
    
    async def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all registered services
        
        Returns:
            Dictionary mapping service names to initialization results
        """
        results = {}
        
        for name, service in self.services.items():
            try:
                result = await service.initialize()
                results[name] = result
                if result:
                    self.logger.info(f"Service {name} initialized successfully")
                else:
                    self.logger.error(f"Service {name} initialization failed")
            except Exception as e:
                results[name] = False
                self.logger.error(f"Service {name} initialization error: {e}")
        
        return results
    
    async def shutdown_all(self) -> None:
        """Shutdown all registered services"""
        for name, service in self.services.items():
            try:
                await service.shutdown()
                self.logger.info(f"Service {name} shutdown completed")
            except Exception as e:
                self.logger.error(f"Service {name} shutdown error: {e}")
    
    async def health_check_all(self) -> Dict[str, HealthCheck]:
        """
        Perform health check on all services
        
        Returns:
            Dictionary mapping service names to health check results
        """
        results = {}
        
        for name, service in self.services.items():
            try:
                health_check = await service.health_check()
                results[name] = health_check
            except Exception as e:
                results[name] = HealthCheck(
                    service_name=name,
                    status=ServiceStatus.UNHEALTHY,
                    message=f"Health check error: {str(e)}",
                    timestamp=datetime.now(timezone.utc)
                )
        
        return results
    
    def get_service(self, service_name: str) -> Optional[BaseService]:
        """Get service by name"""
        return self.services.get(service_name)
