from pyngrok import ngrok
import time
import sys

def start_tunnel(port=8502):
    """
    Starts an ngrok tunnel to the specified port.
    """
    try:
        # Open a HTTP tunnel on the default port 8502
        public_url = ngrok.connect(port).public_url
        print(f"\n========================================================")
        print(f"🌍 Your MOBILE app is now live on the internet!")
        print(f"👉 Public URL: {public_url}")
        print(f"========================================================\n")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping tunnel...")
            ngrok.disconnect(public_url)
            
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        print("Note: You might need to sign up for a free ngrok account and run 'ngrok config add-authtoken <token>' if you haven't already.")

if __name__ == "__main__":
    port = 8502
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_tunnel(port)
