untyped
global function chaTTS_Init

const string URL_LISTENER = "http://127.0.0.1:2222/" // has to match url and port as defined in the exe_wrapper
const table<int, string> voiceIndex = {
	[0] = "cv_chaTTS_uniform_voice",
	[1] = "cv_chaTTS_self_voice",
	[2] = "cv_chaTTS_party_voice",
	[3] = "cv_chaTTS_friend_voice",
	[4] = "cv_chaTTS_team_voice",
	[5] = "cv_chaTTS_opp_voice",
	[6] = "cv_chaTTS_ally_voice"
}

void function debugPrint( string text ){
	printt( "[chaTTS] " + text )
}

void function chaTTS_Init(){
	dtool_loadFriendsAndParty() // this requires the dtools !!
	AddCallback_OnReceivedSayTextMessage( chathook )
	debugPrint( "Initialized! :-)" )
}

bool function makeTTS( int voiceIndex, string voice, string text ){
    table state = {
        finished = false,
        successful = false
    }

    HttpRequest request
    request.method = HttpRequestMethod.POST
    request.url = URL_LISTENER + "/makeTTS"

	// Send data to get processed
    request.queryParameters[ "message" ]  <- [ text ]
	request.queryParameters[ "voice" ] 	  <- [ voice ]
	request.queryParameters[ "position" ] <- [ voiceIndex.tostring() ]

    void functionref( HttpRequestResponse ) onSuccess = void function ( HttpRequestResponse response ) : ( state ){
        debugPrint( "Request was successful" )
	
        state.finished = true
		if( response.statusCode == 200 )
			state.successful = true
		else 
			state.successful = false
	}

	// Server throws an error if e.g the voice is not valid
    void functionref( HttpRequestFailure ) onFailure = void function ( HttpRequestFailure failure ) : ( state ){
        debugPrint( "Request was *not* successful" )
        debugPrint( format( "[%i] Failed to send request to listener server: %s", failure.errorCode, failure.errorMessage ) )

        state.finished = true
		state.successful = false
    }

    NSHttpRequest( request, onSuccess, onFailure )
	
    while( !state.finished )
        wait 0
	
    return expect bool( state.successful )
} 

////////////////////////////////////////////////////////////////////////////////////

int function getVoiceIndexForPlayer( ClClient_MessageStruct ms ){
	// uniform
	if( GetConVarBool( "cv_chaTTS_use_uniform_voice" ) )
		return 0

	// same priority as ccmuv2
	// self
	if( ms.player == GetLocalClientPlayer() )
		return 1

	// party
	if( dtool_inParty( ms.player.GetPlayerName() ) )
		return 2

	// friend
	if( dtool_isFriend( ms.player.GetPlayerName() ) )
		return 3

	// teamchat
	if( ms.isTeam )
		return 4

	// opp
	if( dtool_isEnemy( ms.player ) )
		return 5
	else // ally
		return 6

	// Fallback
	return 0
}

string function getVoiceFromIndex( int index ){
	// Get ConVar from voice index
	if( index in voiceIndex )
		return GetConVarString( voiceIndex[index] )

	// Fallback
	return GetConVarString( "cv_chaTTS_uniform_voice" )
}

void function playTTS( int voiceIndex ){
	GetLocalClientPlayer().ClientCommand( 
		format( 
			"playvideo bik_output_pos_%i 1 1", 
			voiceIndex 
		) 
	)
}

////////////////////////////////////////////////////////////////////////////////////

ClClient_MessageStruct function chathook( ClClient_MessageStruct ms ){
	// Get the right voice for the player and config
	int voiceIndex = getVoiceIndexForPlayer( ms )
	string voice = getVoiceFromIndex( voiceIndex )

	// Try to send request to create TTS file
	bool successful = makeTTS( voiceIndex, voice, ms.message )
	if( successful )
		playTTS( voiceIndex )

	return ms
}