# +++ Modified By Yato [telegram username: @i_killed_my_clan & @ProYato] +++ # aNDI BANDI SANDI JISNE BHI CREDIT HATAYA USKI BANDI RAndi 
import os
import asyncio
import base64
from config import *
from pyrogram import Client, filters
from pyrogram.types import Message, User, ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, ChatAdminRequired, RPCError, UserNotParticipant
from database.database import set_approval_off, is_approval_off
from helper_func import *

# Default settings
APPROVAL_WAIT_TIME = 5  # seconds 
AUTO_APPROVE_ENABLED = True  # Toggle for enabling/disabling auto approval 

async def get_user_client():
    global user_client
    if user_client is None:
        user_client = UserClient("userbot", session_string=USER_SESSION, api_id=APP_ID, api_hash=API_HASH)
        await user_client.start()
    return user_client

@Client.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    global AUTO_APPROVE_ENABLED

    if not AUTO_APPROVE_ENABLED:
        return

    chat = message.chat
    user = message.from_user

    # check agr approval of hai us chnl m
    if await is_approval_off(chat.id):
        print(f"Auto-approval is OFF for channel {chat.id}")
        return

    print(f"{user.first_name} requested to join {chat.title}")
    
    await asyncio.sleep(APPROVAL_WAIT_TIME)

    # Check if user is already a participant before approving
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in ["member", "administrator", "creator"]:
            print(f"User {user.id} is already a participant of {chat.id}, skipping approval.")
            return
    except UserNotParticipant:
        # User is not a member, handle accordingly
        pass

        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    
    if APPROVED == "on":
        # চ্যাটের আসল আইডিটি স্ট্রিং হিসেবে নেওয়া হলো (যেমন: -1003584836363)
        chat_id_str = str(chat.id)
        
        # আইডিটিকে Base64 এ কনভার্ট করে শেষের '=' চিহ্ন (প্যাডিং) সরিয়ে দেওয়া হলো
        encoded_id = base64.urlsafe_b64encode(chat_id_str.encode('ascii')).decode('ascii').rstrip('=')
        
        # আপনার লিংকের ফরম্যাট অনুযায়ী অটোমেটিক লিংক তৈরি
        # (এখানে queenlinksbot এর জায়গায় চাইলে আপনার বটের ইউজারনেমও দিতে পারেন)
        dynamic_link = f"https://t.me/queenlinksbot?start=req_{encoded_id}"

        buttons = [
            [InlineKeyboardButton('• ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs •', url='https://t.me/koreandrama006')],
            [InlineKeyboardButton(f'• ᴊᴏɪɴ {chat.title} •', url=dynamic_link)]
        ]
        markup = InlineKeyboardMarkup(buttons)
        caption = f"<b>ʜᴇʏ {user.mention()},\n\n<blockquote> ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ _{chat.title} ʜᴀs ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ.</blockquote> </b>"
        
        await client.send_photo(
            chat_id=user.id,
            photo='https://telegra.ph/file/f3d3aff9ec422158feb05-d2180e3665e0ac4d32.jpg',
            caption=caption,
            reply_markup=markup
        )


@Client.on_message(filters.command("reqtime") & is_owner_or_admin)
async def set_reqtime(client, message: Message):
    global APPROVAL_WAIT_TIME
    
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Usage: <code>/reqtime {seconds}</code>")
    
    APPROVAL_WAIT_TIME = int(message.command[1])
    await message.reply_text(f"✅ Request approval time set to <b>{APPROVAL_WAIT_TIME}</b> seconds.")

@Client.on_message(filters.command("reqmode") & is_owner_or_admin)
async def toggle_reqmode(client, message: Message):
    global AUTO_APPROVE_ENABLED
    
    if len(message.command) != 2 or message.command[1].lower() not in ["on", "off"]:
        return await message.reply_text("Usage: <code>/reqmode on</code> or <code>/reqmode off</code>")
    
    mode = message.command[1].lower()
    AUTO_APPROVE_ENABLED = (mode == "on")
    status = "enabled ✅" if AUTO_APPROVE_ENABLED else "disabled ❌"
    await message.reply_text(f"Auto-approval has been {status}.")

@Client.on_message(filters.command("approveoff") & is_owner_or_admin)
async def approve_off_command(client, message: Message):
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("Usage: <code>/approveoff {channel_id}</code>")
    channel_id = int(message.command[1])
    success = await set_approval_off(channel_id, True)
    if success:
        await message.reply_text(f"✅ Auto-approval is now <b>OFF</b> for channel <code>{channel_id}</code>.")
    else:
        await message.reply_text(f"❌ Failed to set auto-approval OFF for channel <code>{channel_id}</code>.")

@Client.on_message(filters.command("approveon") & is_owner_or_admin)
async def approve_on_command(client, message: Message):
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("Usage: <code>/approveon {channel_id}</code>")
    channel_id = int(message.command[1])
    success = await set_approval_off(channel_id, False)
    if success:
        await message.reply_text(f"✅ Auto-approval is now <b>ON</b> for channel <code>{channel_id}</code>.")
    else:
        await message.reply_text(f"❌ Failed to set auto-approval ON for channel <code>{channel_id}</code>.")
