
from xero import Xero

xero = Xero(credentials)
organisations = xero.organisations.all()
print(organisations)
