import pyramid_handlers
from crawler_app.controllers.base_controller import BaseController
from crawler_app.services.account_service import AccountService
from crawler_app.viewmodels.register_viewmodel import RegisterViewModel
from crawler_app.viewmodels.signin_viewmodel import SigninViewModel
import crawler_app.infrastructure.cookie_auth as cookie_auth

#Home page controller, routes to register and sign in

class HomeController(BaseController):

    @pyramid_handlers.action(renderer='templates/home/index.pt')
    def index(self):
        return {'value': 'HOME'}


    @pyramid_handlers.action(renderer='templates/account/signin.pt',
                             request_method='GET',
                             name='signin')
    def signin_get(self):
        return SigninViewModel().to_dict()


    @pyramid_handlers.action(renderer='templates/account/signin.pt',
                             request_method='POST',
                             name='signin')
    def signin_post(self):
        vm = SigninViewModel()
        vm.from_dict(self.data_dict)

        account = AccountService.get_authenticated_account(vm.username, vm.password)
        if not account:
            vm.error = "username address or password are incorrect."
            return vm.to_dict()

        cookie_auth.set_auth(self.request, account.id)

        return self.redirect('/home')


    @pyramid_handlers.action()
    def logout(self):
        cookie_auth.logout(self.request)
        self.redirect('/home')


    @pyramid_handlers.action(renderer='templates/account/register.pt',
                             request_method='GET',
                             name='register')
    def register_get(self):
        vm = RegisterViewModel()
        return vm.to_dict()


    @pyramid_handlers.action(renderer='templates/account/register.pt',
                             request_method='POST',
                             name='register')
    def register_post(self):
        vm = RegisterViewModel()
        vm.from_dict(self.request.POST)

        vm.validate()
        if vm.error:
            return vm.to_dict()

        account = AccountService.find_account_by_username(vm.username)
        if account:
            vm.error = "An account with this username already exists. " \
                       "Please log in instead."
            return vm.to_dict()

        account = AccountService.create_account(vm.username, vm.password)
 
        self.redirect('/home/signin')