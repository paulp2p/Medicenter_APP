import allure

def mask_otp(otp: str) -> str:
    if not otp:
        return ""
    return "***" + otp[-2:]

def attach_otp_to_allure(otp: str, name: str = "OTP (mask)"):
    if not otp:
        return
    allure.attach(mask_otp(otp), name=name, attachment_type=allure.attachment_type.TEXT)
