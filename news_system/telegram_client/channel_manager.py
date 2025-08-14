#!/usr/bin/env python3
# telegram/channel_manager.py - Manages Telegram channels

import logging
import asyncio
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import config
except ImportError:
    # Fallback import path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    import config
from telegram import Bot, ChatPermissions, ChatMemberUpdated
from telegram.error import TelegramError

logger = logging.getLogger("ChannelManager")

class ChannelManager:
    """
    Manage Telegram channels for news distribution.
    """
    
    def __init__(self, token=None, category=None):
        """
        Initialize the channel manager.
        
        Args:
            token (str, optional): Telegram bot token
            category (str, optional): Category to use for bot selection
        """
        if token:
            self.token = token
        elif category and category in config.TELEGRAM_BOT_TOKENS:
            self.token = config.TELEGRAM_BOT_TOKENS[category]
        else:
            # Default to first available token
            self.token = next(iter(config.TELEGRAM_BOT_TOKENS.values()))
            
        self.bot = Bot(token=self.token)
        
    async def get_channel_info(self, channel_id):
        """
        Get information about a channel.
        
        Args:
            channel_id (str): Channel ID or username
            
        Returns:
            dict: Channel information
        """
        try:
            chat = await self.bot.get_chat(channel_id)
            return {
                "id": chat.id,
                "type": chat.type,
                "title": chat.title,
                "username": chat.username,
                "description": chat.description,
                "invite_link": chat.invite_link,
                "permissions": chat.permissions.to_dict() if chat.permissions else None
            }
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None
            
    async def create_channel(self, title, description=None):
        """
        Create a new channel.
        Note: This cannot be done through the Bot API, requires user interaction.
        
        Returns:
            str: Instructions for manual channel creation
        """
        return """
        Telegram bots cannot create channels directly. To create a channel:
        
        1. Open Telegram app
        2. Click on the pencil icon (new message)
        3. Select "New Channel"
        4. Enter channel name and description
        5. Make the channel public or private
        6. Add your bot as an administrator
        7. Grant the bot the following permissions:
           - Post messages
           - Edit messages
           - Delete messages
           - Add admins (if needed)
        """
        
    async def add_bot_as_admin(self, channel_id):
        """
        Instructions to add the bot as an admin to a channel.
        
        Args:
            channel_id (str): Channel ID
            
        Returns:
            str: Instructions
        """
        bot_info = await self.bot.get_me()
        bot_username = bot_info.username
        
        return f"""
        To add the bot @{bot_username} as an admin to your channel:
        
        1. Open your channel in Telegram
        2. Click on the channel name at the top
        3. Select "Administrators"
        4. Click "Add Administrator"
        5. Search for @{bot_username}
        6. Grant these permissions:
           - Post messages
           - Edit messages
           - Delete messages
           - Add admins (if needed)
        """
        
    async def check_bot_permissions(self, channel_id):
        """
        Check if the bot has the necessary permissions in a channel.
        
        Args:
            channel_id (str): Channel ID
            
        Returns:
            dict: Permissions the bot has
        """
        try:
            bot_info = await self.bot.get_me()
            bot_id = bot_info.id
            
            member = await self.bot.get_chat_member(channel_id, bot_id)
            
            # Extract permissions
            can_post = False
            if member.status == "administrator":
                can_post = member.can_post_messages
                
            return {
                "is_member": member.status in ["administrator", "member", "creator"],
                "is_admin": member.status == "administrator",
                "is_creator": member.status == "creator",
                "can_post_messages": can_post,
                "full_permissions": member.to_dict()
            }
        except Exception as e:
            logger.error(f"Error checking permissions for {channel_id}: {e}")
            return {
                "is_member": False,
                "is_admin": False,
                "is_creator": False,
                "can_post_messages": False,
                "error": str(e)
            }
            
    async def channel_exists(self, channel_id):
        """
        Check if a channel exists and the bot is a member.
        
        Args:
            channel_id (str): Channel ID
            
        Returns:
            bool: True if channel exists and bot is a member
        """
        try:
            chat = await self.bot.get_chat(channel_id)
            return True
        except Exception:
            return False

# Example usage
async def setup_channels():
    """
    Setup channels for news categories.
    """
    manager = ChannelManager()
    
    # Check each channel in config
    for category, channel_id in config.TELEGRAM_CHANNELS.items():
        exists = await manager.channel_exists(channel_id)
        
        if exists:
            logger.info(f"Channel for {category} exists: {channel_id}")
            # Check permissions
            perms = await manager.check_bot_permissions(channel_id)
            if perms["can_post_messages"]:
                logger.info(f"Bot has posting permissions in {channel_id}")
            else:
                logger.warning(f"Bot lacks posting permissions in {channel_id}")
                instructions = await manager.add_bot_as_admin(channel_id)
                logger.info(f"Instructions to add bot as admin: {instructions}")
        else:
            logger.warning(f"Channel for {category} does not exist: {channel_id}")
            create_instructions = await manager.create_channel(f"{category.title()} News")
            logger.info(f"Channel creation instructions: {create_instructions}")

if __name__ == "__main__":
    # Test channel setup
    asyncio.run(setup_channels())