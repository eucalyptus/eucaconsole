from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard
from pages.loginpage import LoginPage
from pages.keypair.keypairdetail import KeypairDetailPage
from pages.keypair.keypairview import KeypairView
from dialogs.keypair_dialogs import CreateKeypairDialog, DeleteKeypairModal, ImportKeypairDialog



class GuiIAM(GuiTester):

    def __init__(self, webdriver_url, console_url, account="ui-test-acct-00", user="admin", password="mypassword0"):
        super(GuiEC2, self).__init__(webdriver_url, console_url, account=account, user=user, password=password)
