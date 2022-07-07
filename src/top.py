import onetimepass as otp

my_secret = 'EZNVTPVMG3PTDRTE5X6IWBK2CDF3DIPH'
my_token = otp.get_totp(my_secret)
print(my_token)