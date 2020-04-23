<h2> Whiskey upload API (tags & places, filtration)</h2>

- User Registration
- User Token Authentication
- User Details display (based on the token loaded)
- API root for Tag API, Place Upload API, Whiskey Upload API, Image File API
- Tag API -> create tags to assign to your whiskey when POSTing recipe
    - Display detail of the tag and Update or Delete (if owner)
- Place API -> create places to assign to your whiskey when POSTing recipe
    - Display detail of the place and Update or Delete (if owner)
- Whiskey API ->
    - Upload and name whiskeys
    - Add Tags & Places to your whiskeys
    - Add description, style (ie burboun, rye, etc), price
    - Add an Image of your whiskey (upload a file)
    - Display detail of the whiskey and Update or Delete (if owner)
- Filtering based on tags & places for both Private and Public API

<h2>Deployed to Heroku using Git</h2>

<b>ROOT URL: http://wiseguy-whiskey.herokuapp.com/

URL Endpoints:</b>

-	/api/user/create/				
-	/api/user/token/					
-	/api/user/me/				
-	/api/whiskey/				
-	/api/whiskey/tags/					
-	/api/whiskey/tags/pk/				
-	/api/whiskey/places/				
-	/api/whiskey/places/pk/				
-	/api/whiskey/whiskeys/				
-	/api/whiskey/whiskeys/pk/				
-	/api/whiskey/whiskeys/pk/upload-image/		
-	/api/whiskey/whiskeys/?tags=pk&places=pk
