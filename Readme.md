This script posts a random card from the *Disney Lorcana Trading Card Game* to Mastodon and Bluesky.  
It doesn't need any external libraries.  
The source of the card data is [LorcanaJSON](https://lorcanajson.org).  

Copy 'credentials.json.example', rename it to 'credentials.json', and fill in your account details to enable posting.   

Commandline arguments:  
* **update**: Update the stored card data if a new version exists, and (re)create a posting schedule
* **forceupdate**: Same as update, except it doesn't check for a new version, it always updates
* **rebuildschedule**: Create a new randomized posting schedule, making sure already-posted cards aren't posted again
* **post**: Actually post a random *Disney Lorcana TCG* card to Mastodon and Bluesky

This project is **not** affiliated with, or recognized, sponsored, or endorsed by Disney or Ravensburger in any way.  
This project uses trademarks and/or copyrights associated with Disney Lorcana TCG, used under [Ravensburger’s Community Code Policy](https://cdn.ravensburger.com/lorcana/community-code-en). 
We are expressly prohibited from charging you to use or access this content. This project is not published, endorsed, or specifically approved by Disney or Ravensburger. 
For more information about Disney Lorcana TCG, visit https://www.disneylorcana.com/en-US/
