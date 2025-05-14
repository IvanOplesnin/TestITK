from asyncio import Lock


class LockWallet:

    def __init__(self):
        self.wallets: dict[str, Lock] = {}

    def get_lock(self, wallet: str) -> Lock:
        return self.wallets.setdefault(wallet, Lock())


lock_wallet = LockWallet()
