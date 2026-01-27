untyped
global function chaTTSSettings_Init

const array<string> boolSettings = [ "No", "Yes" ]

void function chaTTSSettings_Init(){
	ModSettings_AddModTitle( 	"^FFFFFF00[chaTTS] ^cbaed400T^b99ec100T^a68ead00S ^947e9a00C^826e8700h^705e7400a^5d4e6000t" )

	ModSettings_AddModCategory( "^FFFFFF00> Uniformity" )
	AddConVarSettingEnum(       "cv_chaTTS_use_uniform_voice",      "^FFFFFF00cv_chaTTS_use_uniform_voice",     boolSettings )
	AddConVarSetting(           "cv_chaTTS_uniform_voice",          "^FFFFFF00cv_chaTTS_uniform_voice",         "string" )

    ModSettings_AddModCategory( "^FFFFFF00> Specifics" )
	AddConVarSetting(           "cv_chaTTS_team_voice",             "^FFFFFF00cv_chaTTS_team_voice",	        "string" )
    AddConVarSetting(           "cv_chaTTS_ally_voice",             "^FFFFFF00cv_chaTTS_ally_voice",	        "string" )
	AddConVarSetting(           "cv_chaTTS_self_voice",             "^FFFFFF00cv_chaTTS_self_voice",	        "string" )
	AddConVarSetting(           "cv_chaTTS_friend_voice",           "^FFFFFF00cv_chaTTS_friend_voice",	        "string" )
	AddConVarSetting(           "cv_chaTTS_party_voice",            "^FFFFFF00cv_chaTTS_party_voice",	        "string" )
	AddConVarSetting(           "cv_chaTTS_opp_voice",              "^FFFFFF00cv_chaTTS_opp_voice",	            "string" )

}