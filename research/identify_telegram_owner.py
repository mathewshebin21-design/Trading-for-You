"""One-time private-chat pairing helper. Token comes from secure environment."""
import os
import secrets
import time
from telegram_paper_bot import TelegramAPI

if __name__=='__main__':
    try:
        api=TelegramAPI(os.environ['TELEGRAM_BOT_TOKEN']);bot=api.call('getMe',{})
        if api.call('getWebhookInfo',{}).get('url'):raise RuntimeError('Use a dedicated bot without webhook')
        code=secrets.token_hex(12)
        print('Send this exact command in your PRIVATE chat with @'+bot['username']+':')
        print('/setup '+code,flush=True)
        print('Pairing expires in 5 minutes. No trade commands are active.',flush=True)
        end=time.monotonic()+300;offset=0
        while time.monotonic()<end:
            for u in api.call('getUpdates',{'offset':offset,'timeout':10,'allowed_updates':['message']}):
                offset=u['update_id']+1;m=u.get('message',{});f=m.get('from',{});chat=m.get('chat',{})
                if (m.get('text')=='/setup '+code and chat.get('type')=='private' and
                    f.get('id')==chat.get('id') and not f.get('is_bot') and abs(time.time()-m.get('date',0))<120):
                    print('Set TELEGRAM_OWNER_ID='+str(f['id'])+' in secure hosting settings.')
                    raise SystemExit(0)
        raise RuntimeError('Pairing expired')
    except Exception:raise SystemExit('Pairing failed. Check bot configuration/network. No credentials printed.') from None
