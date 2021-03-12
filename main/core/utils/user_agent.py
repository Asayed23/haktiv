from user_agents import parse

def get_user_agent(request):
    return parse(request.META["HTTP_USER_AGENT"])

def get_os(request):
    os_data = get_user_agent(request=request)
    return dict(os=os_data.os.family, device=os_data.device.family)

def get_browser(request):
    browser_data = get_user_agent(request=request)
    return dict(browser=browser_data.browser.family, version=browser_data.browser.version,
                device_model=browser_data.device.model)