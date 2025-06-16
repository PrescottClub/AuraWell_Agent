#!/usr/bin/env python3
"""
WebSocket Integration Tests for AuraWell Phase IV

Tests WebSocket streaming functionality including:
- Connection establishment
- Message streaming
- Status management
- Error handling
- Concurrent connections
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
import websockets
import pytest
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketTester:
    """WebSocket functionality tester"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    async def test_connection_establishment(self, user_id: str = "test_user_001") -> Dict[str, Any]:
        """Test WebSocket connection establishment"""
        logger.info(f"Testing WebSocket connection for user: {user_id}")
        
        uri = f"{self.base_url}/ws/chat/{user_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Wait for welcome message
                welcome_message = await websocket.recv()
                welcome_data = json.loads(welcome_message)
                
                result = {
                    "test": "connection_establishment",
                    "user_id": user_id,
                    "success": True,
                    "welcome_message": welcome_data,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"✅ Connection established successfully for {user_id}")
                return result
                
        except Exception as e:
            result = {
                "test": "connection_establishment",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"❌ Connection failed for {user_id}: {e}")
            return result
    
    async def test_health_chat_streaming(self, user_id: str = "test_user_002") -> Dict[str, Any]:
        """Test health chat with streaming response"""
        logger.info(f"Testing health chat streaming for user: {user_id}")
        
        uri = f"{self.base_url}/ws/chat/{user_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Skip welcome message
                await websocket.recv()
                
                # Send health chat message
                chat_message = {
                    "type": "health_chat",
                    "data": {
                        "message": "我最近觉得很累，有什么健康建议吗？",
                        "context": {"mood": "tired", "activity_level": "low"}
                    },
                    "conversation_id": "test_conv_001",
                    "active_member_id": user_id
                }
                
                await websocket.send(json.dumps(chat_message, ensure_ascii=False))
                logger.info("📤 Sent health chat message")
                
                # Collect streaming responses
                stream_tokens = []
                status_updates = []
                
                # Collect responses for up to 30 seconds
                timeout = 30
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        response_data = json.loads(response)
                        
                        if response_data.get("type") == "chat_stream":
                            stream_tokens.append(response_data)
                        elif response_data.get("type") == "status_update":
                            status_updates.append(response_data)
                            
                            # Stop if we get "done" status
                            if response_data.get("status") == "done":
                                break
                                
                    except asyncio.TimeoutError:
                        break
                    except websockets.exceptions.ConnectionClosed:
                        break
                
                # Verify we got streaming tokens
                success = len(stream_tokens) > 0 and len(status_updates) > 0
                
                result = {
                    "test": "health_chat_streaming",
                    "user_id": user_id,
                    "success": success,
                    "stream_tokens_count": len(stream_tokens),
                    "status_updates_count": len(status_updates),
                    "first_3_tokens": [t.get("delta", "") for t in stream_tokens[:3]],
                    "final_status": status_updates[-1] if status_updates else None,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    logger.info(f"✅ Health chat streaming successful: {len(stream_tokens)} tokens received")
                else:
                    logger.error(f"❌ Health chat streaming failed: no tokens received")
                
                return result
                
        except Exception as e:
            result = {
                "test": "health_chat_streaming",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"❌ Health chat streaming failed for {user_id}: {e}")
            return result
    
    async def test_general_chat(self, user_id: str = "test_user_003") -> Dict[str, Any]:
        """Test general chat functionality"""
        logger.info(f"Testing general chat for user: {user_id}")
        
        uri = f"{self.base_url}/ws/chat/{user_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Skip welcome message
                await websocket.recv()
                
                # Send general chat message
                chat_message = {
                    "type": "general_chat",
                    "data": {
                        "message": "你好，今天天气怎么样？"
                    },
                    "conversation_id": "test_conv_002"
                }
                
                await websocket.send(json.dumps(chat_message, ensure_ascii=False))
                logger.info("📤 Sent general chat message")
                
                # Collect responses
                responses = []
                timeout = 15
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                        response_data = json.loads(response)
                        responses.append(response_data)
                        
                        # Stop if we get "done" status
                        if (response_data.get("type") == "status_update" and 
                            response_data.get("status") == "done"):
                            break
                            
                    except asyncio.TimeoutError:
                        break
                
                success = len(responses) > 0
                
                result = {
                    "test": "general_chat",
                    "user_id": user_id,
                    "success": success,
                    "responses_count": len(responses),
                    "responses": responses,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    logger.info(f"✅ General chat successful: {len(responses)} responses received")
                else:
                    logger.error(f"❌ General chat failed: no responses received")
                
                return result
                
        except Exception as e:
            result = {
                "test": "general_chat",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"❌ General chat failed for {user_id}: {e}")
            return result
    
    async def test_concurrent_connections(self, user_count: int = 5) -> Dict[str, Any]:
        """Test multiple concurrent WebSocket connections"""
        logger.info(f"Testing {user_count} concurrent WebSocket connections")
        
        async def single_user_test(user_id: str):
            """Test single user connection"""
            uri = f"{self.base_url}/ws/chat/{user_id}"
            
            try:
                async with websockets.connect(uri) as websocket:
                    # Get welcome message
                    welcome = await websocket.recv()
                    
                    # Send a simple message
                    message = {
                        "type": "get_status",
                        "data": {}
                    }
                    await websocket.send(json.dumps(message))
                    
                    # Get response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    return {
                        "user_id": user_id,
                        "success": True,
                        "response": response_data
                    }
                    
            except Exception as e:
                return {
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Create concurrent tasks
        tasks = []
        for i in range(user_count):
            user_id = f"concurrent_user_{i+1:03d}"
            task = single_user_test(user_id)
            tasks.append(task)
        
        try:
            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_connections = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
            success_rate = (successful_connections / user_count) * 100
            
            result = {
                "test": "concurrent_connections",
                "user_count": user_count,
                "successful_connections": successful_connections,
                "success_rate": success_rate,
                "success": success_rate >= 80,  # Consider success if 80%+ connections work
                "individual_results": results,
                "timestamp": datetime.now().isoformat()
            }
            
            if success_rate >= 80:
                logger.info(f"✅ Concurrent connections test passed: {success_rate:.1f}% success rate")
            else:
                logger.error(f"❌ Concurrent connections test failed: {success_rate:.1f}% success rate")
            
            return result
            
        except Exception as e:
            result = {
                "test": "concurrent_connections",
                "user_count": user_count,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"❌ Concurrent connections test failed: {e}")
            return result
    
    async def test_member_switch(self, user_id: str = "test_user_004") -> Dict[str, Any]:
        """Test member switching functionality"""
        logger.info(f"Testing member switch for user: {user_id}")
        
        uri = f"{self.base_url}/ws/chat/{user_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Skip welcome message
                await websocket.recv()
                
                # Send member switch message
                switch_message = {
                    "type": "switch_member",
                    "data": {
                        "target_member_id": "family_member_001"
                    }
                }
                
                await websocket.send(json.dumps(switch_message))
                logger.info("📤 Sent member switch message")
                
                # Get response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                success = (response_data.get("type") == "status_update" and 
                          response_data.get("status") == "done")
                
                result = {
                    "test": "member_switch",
                    "user_id": user_id,
                    "success": success,
                    "response": response_data,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    logger.info(f"✅ Member switch successful")
                else:
                    logger.error(f"❌ Member switch failed")
                
                return result
                
        except Exception as e:
            result = {
                "test": "member_switch",
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"❌ Member switch failed for {user_id}: {e}")
            return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all WebSocket tests"""
        logger.info("🚀 Starting comprehensive WebSocket tests")
        
        all_results = []
        
        # Test 1: Connection establishment
        result1 = await self.test_connection_establishment()
        all_results.append(result1)
        
        # Test 2: Health chat streaming
        result2 = await self.test_health_chat_streaming()
        all_results.append(result2)
        
        # Test 3: General chat
        result3 = await self.test_general_chat()
        all_results.append(result3)
        
        # Test 4: Member switch
        result4 = await self.test_member_switch()
        all_results.append(result4)
        
        # Test 5: Concurrent connections
        result5 = await self.test_concurrent_connections(user_count=10)
        all_results.append(result5)
        
        # Calculate overall success
        successful_tests = sum(1 for r in all_results if r.get("success", False))
        total_tests = len(all_results)
        overall_success_rate = (successful_tests / total_tests) * 100
        
        summary = {
            "overall_success": overall_success_rate >= 80,
            "success_rate": overall_success_rate,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "test_results": all_results,
            "timestamp": datetime.now().isoformat()
        }
        
        if overall_success_rate >= 80:
            logger.info(f"🎉 WebSocket tests PASSED: {overall_success_rate:.1f}% success rate")
        else:
            logger.error(f"❌ WebSocket tests FAILED: {overall_success_rate:.1f}% success rate")
        
        return summary


async def main():
    """Main test function"""
    print("🌟 AuraWell Phase IV - WebSocket Integration Tests")
    print("=" * 60)
    
    # Check if server is running
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/health") as response:
                if response.status != 200:
                    print("❌ Server not responding. Please start the API server first.")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please ensure the API server is running on http://localhost:8000")
        return
    
    # Run WebSocket tests
    tester = WebSocketTester()
    results = await tester.run_all_tests()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"websocket_test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Test report saved: {report_file}")
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"  Total tests: {results['total_tests']}")
    print(f"  Successful: {results['successful_tests']}")
    print(f"  Success rate: {results['success_rate']:.1f}%")
    
    if results['overall_success']:
        print(f"🏆 Phase IV WebSocket tests PASSED!")
    else:
        print(f"⚠️ Phase IV WebSocket tests need attention!")


if __name__ == "__main__":
    asyncio.run(main()) 