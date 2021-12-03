INFORMATION ABOUT PORTS OF TOR-BROWSERS:


Every tor-browser is configured with its own SocksPort and ControlPort to take multiple traces at a same time without interfering.
You can either set/change ports in Tor Browser under about:config or manually under /WebsiteFingerprinting/src/tortracer/tor-browsers/tor-browser-<NUMBER>/Browser/TorBrowser/Data/Browser/profile.default/prefs.js.
Already existing folder (number 1-16) include in prefs.js user_pref("network.proxy.socks_port", 9850); and user_pref("extensions.torlauncher.control_port", 9158);. 
Just change the value to your prefered port. 
New created (copied) tor-browser folder don't have these user_prefs. 
Copy them into prefs.js and set your prefered ports.

tor-browser-1:
SocksPort	9150
ControlPort	9151

tor-browser-2:
SocksPort	9250
ControlPort	9152

tor-browser-3:
SocksPort	9350
ControlPort	9153

tor-browser-4:
SocksPort	9450
ControlPort	9154

tor-browser-5:
SocksPort	9550
ControlPort	9155

tor-browser-6:
SocksPort	9650
ControlPort	9156

tor-browser-7:
SocksPort	9750
ControlPort	9157

tor-browser-8:
SocksPort	9850
ControlPort	9158

tor-browser-9:
SocksPort	9950
ControlPort	9159

tor-browser-10:
SocksPort	10050
ControlPort	9160

tor-browser-11:
SocksPort	10150
ControlPort	9161

tor-browser-12:
SocksPort	10250
ControlPort	9162

tor-browser-13:
SocksPort	10350
ControlPort	9163

tor-browser-14:
SocksPort	10450
ControlPort	9164

tor-browser-15:
SocksPort	10550
ControlPort	9165

tor-browser-16:
SocksPort	10650
ControlPort	9166
