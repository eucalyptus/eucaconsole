from pages.detailpage import DetailPage


class ELBDetailPage(DetailPage):

    def __init__(self, tester, load_balancer_name):
        """
        Initiates ELB Detail page object.
        :param load_balancer_name:
        :param tester:
        """
        self.load_balancer_name = load_balancer_name
        self.tester = tester
