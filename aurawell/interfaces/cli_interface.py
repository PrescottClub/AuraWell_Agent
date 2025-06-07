import asyncio
import sys
from aurawell.agent.conversation_agent import ConversationAgent

def main():
    """
    命令行界面的主入口点。
    """
    # 简单的用户ID，未来可以替换为登录系统
    user_id = "cli_user_001" 
    print("Welcome to AuraWell CLI!")
    print(f"Initializing session for user: {user_id}")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("-" * 20)

    agent = ConversationAgent(user_id=user_id)

    # 在Windows上设置事件循环策略以支持asyncio.run
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def chat_loop():
        while True:
            try:
                user_message = input("You: ")
                if user_message.lower() in ["exit", "quit"]:
                    print("AuraWell: Goodbye! Take care of your health.")
                    break
                
                print("AuraWell is thinking...")
                response = await agent.a_run(user_message)
                print(f"AuraWell: {response}")

            except (KeyboardInterrupt, EOFError):
                print("\n\nAuraWell: Goodbye! Session ended.")
                break
    
    try:
        asyncio.run(chat_loop())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 