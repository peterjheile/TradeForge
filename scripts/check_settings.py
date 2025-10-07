###
# Last edit: 10/6/2025
#
# Desc: Quick test to see if settings works and what exactly is printed
###

from app.settings import get_settings

def test_settings(s):

    print("################################################################################")
    print(f"Configured Providers: {s.configured_providers()}")
    print(s)





s = get_settings()
test_settings(s)
