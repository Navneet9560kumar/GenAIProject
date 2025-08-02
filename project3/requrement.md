1= python -m pipx ensurepath
2=
3 ham Deepgram or Twilio logo use kar rahe hai 
Twilog ka use ham call karne ke leye ya ye sab ke leye ham karte use or ham ko need hoti hai ke ham call ar skake is leye Twilog 
Twilog mai aa kar wah s enumber byy karna free kuk creadt mile the is leye waha se leya hai 
install karke fir ham ye karege ke = https://dashboard.ngrok.com/get-started/your-authtoken 

 is per aapna auth lenge or uske badd ham auth lekar = ngrok config add-authtoken 30k9RyDyckqBt59n3hduWMQZ4q2_2ENJbZqL8yyAxULuvamqw

  ye paste kar dnege 

  6 = fir ham jab negok http 5000 ke badd ek url milega use tiwalo ke confir mai jakar paste kar dunga 
  7 = fir ham kay karege vo kar dene ke baad Active  number per aate or aane ke number per tap karke ham log config mai aa jeyegenge or uske baad ham toglle bar mai ham towling bin kar dnege 
  8 or sabse babhi baat agr chnage keya tongrok band keya or dubara start keya to uskaa url chnage ho jayega or or fir config mai jakar chnage karna hoga hamko 

  9 def sts_connect():
      api_key = os.getenv("DEEPGRAM_API_KEY")
      if not api_key:
            raise Exception("DEEPGRAM_API_KEY not set in environment variables")

            sts_ws = websockets.connect(
                  "wss://agent.deepgram.com/v1/agent/converse",
                  subprotocols=["token", api_key]
            )
 ye code jo hai ye ham websocket se connect kar sakte hai 