untyped
global function chaTTSSettings_Init

const array<string> boolSettings = [ "No", "Yes" ]

void function chaTTSSettings_Init(){
	ModSettings_AddModTitle( 	"^FFFFFF00[chaTTS] ^cbaed400T^b99ec100T^a68ead00S ^947e9a00C^826e8700h^705e7400a^5d4e6000t" )

	ModSettings_AddModCategory( "^FFFFFF00> Profanity" )
	AddConVarSettingEnum(       "cv_chaTTS_censor",      			"^FFFFFF00Beep profanity",     					boolSettings )

	ModSettings_AddModCategory( "^FFFFFF00> Uniformity" )
	AddConVarSettingEnum(       "cv_chaTTS_use_uniform_voice",      "^FFFFFF00Use single voice for everything",     boolSettings )
	AddConVarSetting(           "cv_chaTTS_uniform_voice",          "^FFFFFF00Uniform voice",         				"string" )

    ModSettings_AddModCategory( "^FFFFFF00> Specific voices" )
	AddConVarSetting(           "cv_chaTTS_self_voice",             "^FFFFFF00Yourself",	    	  				"string" )
	AddConVarSetting(           "cv_chaTTS_friend_voice",           "^FFFFFF00Friends",	        	  				"string" )
	AddConVarSetting(           "cv_chaTTS_party_voice",            "^FFFFFF00Party members",		  				"string" )

	AddConVarSetting(           "cv_chaTTS_team_voice",             "^FFFFFF00Teamchat",	    	  				"string" )
	AddConVarSetting(           "cv_chaTTS_ally_voice",             "^FFFFFF00Allies",	        	  				"string" )
	AddConVarSetting(           "cv_chaTTS_opp_voice",              "^FFFFFF00Opponents",	    	  				"string" )
}