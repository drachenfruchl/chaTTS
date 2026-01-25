untyped
global function chaTTS_Init


const string URL_LISTENER = "http://127.0.0.1:2222/"
const string URL_LIBRE = "http://127.0.0.1:3333/"

void function debugPrint( string text ){
    printt( "[chaTTS] \x1b[0m" + text )
}

void function chaTTS_Init(){
    AddCallback_OnReceivedSayTextMessage( chathook )
    debugPrint( "Initialized! :-)" )
}

// void function libreServer( string operation ){
//     HttpRequest request
//     request.method = HttpRequestMethod.POST
//     request.url = URL_LISTENER + operation

//     if( operation == "start" ){
//         // https://docs.libretranslate.com/guides/installation/#arguments
//         request.queryParameters[ "load-only" ]        <- [ "en,ru,de" ] // Add more languages if you so please
//         // request.queryParameters[ "frontend-timeout" ] <- [ "500" ]
//         request.queryParameters[ "threads" ]          <- [ "16" ]
//     }

//     void functionref( HttpRequestResponse ) onSuccess = void function ( HttpRequestResponse response ) : (){
//         // Request can still be made successfully and return a statuscode indicating an 'error'
//         // e.g when the libretranslate server is already / not even running and thus return statuscode 418
//         if( response.statusCode != 200 ){
//             string msg = "Request was successful but returned a statuscode other than 200"

//             if( response.body.len() == 0 )
//                 msg += ": " + response.statusCode

//             debugPrint( msg )
//             debugPrint( format( "[%i] %s", response.statusCode, response.body ) )
//             return
//         }

//         // The response body usually contains information about a taken action
//         debugPrint( "Request was successful" )
//         debugPrint( response.body )
//     }

//     void functionref( HttpRequestFailure ) onFailure = void function ( HttpRequestFailure failure ) : (){
//         // This usually occurs because the listen server isnt online
//         // !! Make sure to start it beforehand !!
//         debugPrint( "Request was *not* successful" )
//         debugPrint( format( "[%i] Failed to send request to listener: %s", failure.errorCode, failure.errorMessage ) )
//     }

//     NSHttpRequest( request, onSuccess, onFailure )
// }

// string ornull function translateFromTo( string text, string langTo, string langFrom = "auto" ){
//     table state = {
//         finished = false,
//         data = null
//     }

//     HttpRequest request
//     request.method = HttpRequestMethod.POST
//     request.url = URL_LIBRE + "translate"

//     request.headers[ "Content-Type" ] <- [ "application/json" ]

//     table body = {
//         [ "q" ] = text,
//         [ "source" ] = langFrom,
// 		[ "target" ] = langTo,
// 		[ "format" ] = "text",
// 		[ "alternatives" ] = 3,
// 		[ "api_key" ] = ""
//     }
//     request.body = EncodeJSON( body )

//     void functionref( HttpRequestResponse ) onSuccess = void function ( HttpRequestResponse response ) : ( state ){
//         debugPrint( "Request was successful" )

//         table json = DecodeJSON( response.body )
//         debugPrint( expect string( json[ "translatedText" ] ) )
        
//         state.finished = true
//         state.data = expect string( json[ "translatedText" ] )
//     }

//     void functionref( HttpRequestFailure ) onFailure = void function ( HttpRequestFailure failure ) : ( state ){
//         debugPrint( "Request was *not* successful" )
//         debugPrint( format( "[%i] Failed to send request to libretranslate server: %s", failure.errorCode, failure.errorMessage ) )

//         state.finished = true
//     }

//     NSHttpRequest( request, onSuccess, onFailure )
    
//     while( !state.finished )
//         wait 0
    
//     return expect string ornull( state.data )
// } 

// void function sayIn( string message, string langTo = "ru" ){
//     thread function() : ( message, langTo ){
//         string ornull translatedMsg = translateFromTo( message, langTo )
//         if( !translatedMsg )
//             return
        
//         expect string( translatedMsg )
//         GetLocalClientPlayer().ClientCommand( "say " + translatedMsg )
//     }()
// }


////////////////////////////

ClClient_MessageStruct function chathook( ClClient_MessageStruct ms ){
    string ornull translatedMsg = translateFromTo( ms.message, "de" )
    if( !translatedMsg )
        return ms
    expect string( translatedMsg )

    ms.message += "\n-> " + translatedMsg
    return ms
}