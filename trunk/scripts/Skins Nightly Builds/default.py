# -*- coding: cp1252 -*-

# script constants
__script__       = "Skins Nightly Builds"
__author__       = "Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "15-09-2009"
__version__      = "1.0.0"
__svn_revision__  = "$Revision$".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "20000" #XBMC Babylon


import os
import re
import glob
import urllib
from traceback import print_exc

import xbmc
import xbmcgui

xbmc.log( "[SCRIPT] '%s: Version - %s-r%s' initialized!" % ( __script__, __version__, __svn_revision__ ), xbmc.LOGNOTICE )

SHOW_FILESIZE = False

CWD = os.getcwd().rstrip( ";" )
CACHE_DIR = os.path.join( CWD, "cache" )
try:
    settings = xbmc.Settings( CWD )
    if settings.getSetting( "mode" ) == "1":
        CACHE_DIR = xbmc.translatePath( "special://profile/script_data/%s/cache/" % __script__ )
    if settings.getSetting( "show_filesize" ) == "true":
        SHOW_FILESIZE = True
    settings.setSetting( "ver", "%s-r%s" % ( __version__, __svn_revision__ ) )
except:
    xbmc.log( "[SCRIPT: %s] trouble with 'xbmc.Settings'" % ( __script__ ), xbmc.LOGERROR )
    print_exc()
if not os.path.isdir( CACHE_DIR ):
    os.makedirs( CACHE_DIR )

xbmc.log( "[SCRIPT: %s] home is mapped to: %s" % ( __script__, CWD ), xbmc.LOGNOTICE )
xbmc.log( "[SCRIPT: %s] cache is mapped to: %s" % ( __script__, CACHE_DIR ), xbmc.LOGNOTICE )


def get_installation_of_skins():
    skin_path = xbmc.translatePath( "special://skin" ).strip( os.sep )
    cur_skin  = os.path.basename( skin_path )
    skins_path = os.path.dirname( skin_path )
    if ( not cur_skin ) or ( not os.path.isdir( skin_path ) ) or ( not os.path.isdir( skins_path ) ):
        print "error with [special://skin['%s']]" % xbmc.translatePath( "special://skin" ).strip( os.sep )
        cur_skin  = xbmc.getSkinDir()
        #xbmc default mode
        skin_path = xbmc.translatePath( "special://profile/skin/%s" % cur_skin ).strip( os.sep )
        if ( not os.path.isdir( skin_path ) ):
            #xbmc portable mode
            skin_path = xbmc.translatePath( "special://xbmc/skin/%s" % cur_skin ).strip( os.sep )
        if ( not os.path.isdir( skin_path ) ):
            #last change
            skin_path = xbmc.translatePath( "special://home/skin/%s" % cur_skin ).strip( os.sep )
        skins_path = os.path.dirname( skin_path )

    return cur_skin, skin_path, skins_path

cur_skin, skin_path, skins_path = get_installation_of_skins()


xbmc.log( "[SCRIPT: %s] xbmc current skin is: %s" % ( __script__, cur_skin ), xbmc.LOGNOTICE )
xbmc.log( "[SCRIPT: %s] skin %s is mapped to: %s" % ( __script__, cur_skin, skins_path ), xbmc.LOGNOTICE )

GET_LOCALIZED_STRING = xbmc.Language( CWD ).getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

base_url = "http://www.sshcs.com"
skins_url = base_url + "/xbmc/inc/eva.asp?mode=Skins"

#ajout des depots git a modif pour integration dans les options
git={}
git["aeon"]="http://github.com/temmi2000/aeon/commits/"
git["Alaska"]="http://github.com/HitcherUK/Alaska/commits/"
git["aeon-passion"]="http://github.com/Imaginos/aeon-passion/commits/"


class Github_skin:
    def __init__(self,giturl):
        self.rate = "10 / 10"
        self.hit = ""
        self.thumbs= os.path.join( CACHE_DIR, "Aeon" )#� modifier pour traiter les images
        self.rev_url= "http://github.com/feeds/%s/commits/%s/master" % (giturl.split("/")[3], giturl.split("/")[4])
        self.dl_url= "http://github.com/%s/%s/zipball/master" % (giturl.split("/")[3], giturl.split("/")[4])
        self.type=".zip"
        
    def rev_github( self ):
        try:
<<<<<<< .mine
            if bool( self.rev_url ):
=======
            url = ""
            if skin == "Alaska": url = "http://github.com/feeds/HitcherUK/commits/Alaska/master"
            elif skin == "aeon-passion": url = "http://github.com/feeds/Imaginos/commits/aeon-passion/master"
            if bool( url ):
>>>>>>> .r575
                rss = urllib.urlopen( url, "r" ).read()
                date = re.compile( '<updated>(.*?)</updated>' ).findall( rss )
                if date: return "Build r." + "-".join( date[ 0 ].split( "-" )[ :-1 ] )
        except:
            print_exc()
        return "Build r.OnClick"



aeon_passion = {
    "name": "aeon-passion",
    "build": "",
    "hit": "",
    "rate": "10 / 10",
    "thumbs": os.path.join( CACHE_DIR, "Aeon" ),
    "dl": "http://github.com/Imaginos/aeon-passion/zipball/master",
    "type": ".zip"
    }

alaska = {
    "name": "Alaska",
    "build": "",
    "hit": "",
    "rate": "10 / 10",
    "thumbs": [ "http://files.getdropbox.com/u/435063/alaska/alaska_movies.jpg", "http://files.getdropbox.com/u/435063/alaska/alaska_moviesFA.jpg", "http://files.getdropbox.com/u/435063/alaska/alaska_episodesFA.jpg", "http://files.getdropbox.com/u/435063/alaska/alaska_movieinfoFA.jpg" ],
    "dl": "http://github.com/HitcherUK/Alaska/zipball/master",
    "type": ".zip"
    }

SKINS_GITHUB = git.keys()

print "********************************************** %s **********************************************" % SKINS_GITHUB

class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


def get_browse_dialog( default="", heading="", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value


def dl_build( heading, url, destination ):
    DIALOG_PROGRESS.create( heading, GET_LOCALIZED_STRING( 32890 ) )
    xbmc.log( "[SCRIPT: %s] Downloading started: %s" % ( __script__, heading ), xbmc.LOGNOTICE )
    filepath = ""
    try:
        def _report_hook( count, blocksize, totalsize ):
            _line3_ = ""
            if totalsize > 0:
                _line3_ += GET_LOCALIZED_STRING( 32840 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
            else:
                _line3_ += GET_LOCALIZED_STRING( 32841 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent )
            if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
            else: strPercent = "%s%%" % ( strProgressBar, )
            _line3_ += " | %s" % ( strPercent, )
            #DIALOG_PROGRESS.update( percent, url, destination, _line3_ )
            DIALOG_PROGRESS.update( percent, _line3_, destination, GET_LOCALIZED_STRING( 32890 ) )
            if ( DIALOG_PROGRESS.iscanceled() ):
                raise pDialogCanceled()
        xbmc.log( "[SCRIPT: %s] Downloading: %s to %s" % ( __script__, url, destination ), xbmc.LOGDEBUG )
        fp, h = urllib.urlretrieve( url, destination, _report_hook )
        if h:
            #print h
            xbmc.log( "[SCRIPT: %s] download infos: %s" % ( __script__, h ), xbmc.LOGDEBUG )
            try:
                if "text" in h[ "Content-Type" ]:
                    os.unlink( destination )
                    xbmc.log( "[SCRIPT: %s] Content-Type=%s: %s" % ( __script__, h[ "Content-Type" ], destination ), xbmc.LOGERROR )
            except:
                print_exc()
        filepath = fp
    except pDialogCanceled, error:
        xbmc.log( "[SCRIPT: %s] DIALOG::PROGRESS: %s" % ( __script__, error.msg ), xbmc.LOGWARNING )
        filepath = ""
    except:
        print_exc()
        filepath = ""
    DIALOG_PROGRESS.close()
    return filepath


def get_nightly_skins():
    results = []
    try:
        asp = urllib.urlopen( skins_url, "r" ).read()
        skins = re.compile( '<div class="thumbnails" style="float:left;">(.*?)<hr />', re.DOTALL ).findall( asp )
        for count, skin in enumerate( skins ):
            try:
                infos, dl = re.findall( '<span class="cleanlinks">&nbsp;&nbsp;&nbsp;(.*?)<a href="(.*?)">Download</a>', skin )[ 0 ]
                name, build, hit = infos.strip( " |" ).split( " | " )
                dl = base_url + dl
                rate = str( re.findall( '<img src="(.*?)" border="0" />', skin ).count( "/xbmc/img/goldstar.png" ) ) + " / 10"
                thumbs = [ base_url + uri for uri in re.findall( '<a href="(.*?)" class="floatbox" title=".*?" rev=".*?">', skin ) ]
                results.append( { "name": name.strip(), "build": build.strip(), "hit": hit.strip(), "rate": rate, "thumbs": thumbs, "dl": dl } )
            except:
                print_exc()
    except:
        print_exc()
    return results


class nightly( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        self.save_dir = ""

    def onInit( self ):
        listitems = []
        DIALOG_PROGRESS.create( __script__, GET_LOCALIZED_STRING( 32890 ) )
        DIALOG_PROGRESS.update( 0, GET_LOCALIZED_STRING( 32890 ) )
        try:
            xbmc.log( "[SCRIPT: %s] setting up list skins..." % ( __script__ ), xbmc.LOGNOTICE )
            self.skins = get_nightly_skins()
            #ajoute a la liste les nom de skin github
            for i in git.keys():
                self.skins.append("%s" % i)
            #trie la liste selon la valeur de rate eval( "10 / 10") va donner 1
            try: self.skins.sort( key=lambda s: eval( s[ "rate" ] ), reverse=True )
            except: pass

            total_items = len( self.skins )
            try: diff = int( 100.0 / total_items )
            except: diff = 100
            percent = 0
            for count, skin in enumerate( self.skins ):
                # skin dict = { "name": name, "build": build, "hit": hit, "rate": rate, "thumbs": thumbs, "dl": dl }
                print "********************************************** %s **********************************************" % skin[ "name" ]
                if skin[ "name" ] in SKINS_GITHUB:
                    print "********************************************** GITHUB **********************************************"
                    gitname = skin[ "name" ]
                    giturl = git[gitname]
                    current_git = Github_skin(giturl)
                    skin[ "build" ] = current_git.rev_github()
                    skin[ "hit" ] = current_git.hit
                    skin[ "rate" ] = current_git.rate
                    skin[ "thumbs" ] = current_git.thumbs
                    skin[ "dl" ] = current_git.dl
                    
                percent += diff
                line1 = "Skins: %i / %i" % ( count+1, total_items )
                if not SHOW_FILESIZE:
                    DIALOG_PROGRESS.update( percent, line1, skin[ "name" ] )
                xbmc.log( "[SCRIPT: %s] Listing - %s, %s" % ( __script__, line1, skin[ "name" ] ), xbmc.LOGNOTICE )

                listitem = xbmcgui.ListItem( skin[ "name" ] )

                try:
                    if SHOW_FILESIZE:
                        response = xbmc.executehttpapi( "FileSize(%s)" % skin[ "dl" ] ).replace( "<li>", "" )
                        if response.isdigit():
                            listitem.setProperty( "filesize", GET_LOCALIZED_STRING( 32830 ) % ( ( int( response ) / 1024.0 / 1024.0 ), ) )
                            DIALOG_PROGRESS.update( percent, line1, skin[ "name" ], GET_LOCALIZED_STRING( 32830 ) % ( ( int( response ) / 1024.0 / 1024.0 ), ) )
                        #else:
                        #    print repr( response )
                except:
                    print_exc()

                listitem.setProperty( "build", skin[ "build" ] )
                listitem.setProperty( "hit", skin[ "hit" ] )
                listitem.setProperty( "rate", skin[ "rate" ] )

                thumbs = self.get_thumbnails( skin[ "name" ], skin[ "thumbs" ] )
                listitem.setProperty( "thumbs", thumbs )

                listitems.append( listitem )

                if ( DIALOG_PROGRESS.iscanceled() ):
                    break
        except:
            print_exc()
        DIALOG_PROGRESS.close()
        if listitems:
            self.getControl( 450 ).addItems( listitems )

    def get_thumbnails( self, skin, thumbs=[] ):
        local_dir = ""
        try:
            if thumbs == aeon_passion.get( "thumbs" ):
                xbmc.log( "[SCRIPT: %s] skin - %s, multiimage [%s]" % ( __script__, skin, thumbs ), xbmc.LOGDEBUG )
                return thumbs
            for thumb in thumbs:
                dname = os.path.basename( os.path.dirname( thumb ) )
                fname = os.path.basename( thumb )
                local_dir = os.path.join( CACHE_DIR, dname )
                if not os.path.isdir( local_dir ):
                    os.makedirs( local_dir )
                fpath = os.path.join( local_dir, fname )
                if ( not os.path.isfile( fpath ) ):
                    DIALOG_PROGRESS.update( -1, skin, os.path.join( dname, fname ), GET_LOCALIZED_STRING( 32890 ) )
                    urllib.urlretrieve( thumb, fpath )
        except:
            print_exc()
        xbmc.log( "[SCRIPT: %s] skin - %s, multiimage [%s]" % ( __script__, skin, local_dir ), xbmc.LOGDEBUG )
        return local_dir

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 450:
                pos = self.getControl( 450 ).getSelectedPosition()
                url = self.skins[ pos ][ "dl" ]
                heading = ", ".join( [ self.skins[ pos ][ "name" ], self.skins[ pos ][ "build" ] ] )
                dpath = get_browse_dialog( default=self.save_dir, heading=GET_LOCALIZED_STRING( 32100 ) )
                if dpath:
                    ext = self.skins[ pos ].get( "type", ".rar" )
                    fpath = os.path.join( dpath, self.skins[ pos ][ "name" ] + ext )
                    if xbmcgui.Dialog().yesno( heading, GET_LOCALIZED_STRING( 32130 ), GET_LOCALIZED_STRING( 32140 ), fpath ):
                        filename = dl_build( heading, url, fpath )#fpath
                        filesize = ( os.path.getsize( filename ) / 1024.0 / 1024.0 )
                        if filename and ( not self.skins[ pos ][ "name" ] in ( cur_skin, xbmc.getSkinDir() ) ):
                            xbmc.log( "[SCRIPT: %s] FreeMem - [Free: %i Mb] and [Required: %.2f Mb]" % ( __script__, xbmc.getFreeMem(), ( filesize * 1.5 )  ), xbmc.LOGNOTICE )
                            xbmcgui.Dialog().ok( GET_LOCALIZED_STRING( 32200 ), GET_LOCALIZED_STRING( 32210 ), GET_LOCALIZED_STRING( 32220 ) % xbmc.getFreeMem(), GET_LOCALIZED_STRING( 32230 ) % ( filesize * 1.5 ) )
                            if xbmc.getFreeMem() >= ( filesize  * 1.5 ) :
                                DIALOG_PROGRESS.create( heading, "Extracting...", filename, skins_path )
                                xbmc.log( "[SCRIPT: %s] starting - [XBMC.Extract(%s,%s)]" % ( __script__, filename, skins_path ), xbmc.LOGNOTICE )
                                xbmc.executebuiltin( 'XBMC.Extract(%s,%s)' % ( filename, skins_path, ) )
                                DIALOG_PROGRESS.close()
                                skin_name = self.skins[ pos ][ "name" ]
                                ok_name = skin_name
                                #last_skin = sorted( glob.glob( os.path.join( skins_path, "*" ) ), key=lambda s: os.path.getmtime( s ), reverse=True )
                                #last_skin = os.path.basename( ( last_skin or [ "" ] )[ 0 ] )
                                #if last_skin and last_skin != skin_name: ok_name = last_skin
                                xbmcgui.Dialog().ok( __script__, GET_LOCALIZED_STRING( 32110 ), skins_path, ok_name )
                                xbmc.log( "[SCRIPT: %s] finish - [XBMC.Extract]" % ( __script__ ), xbmc.LOGNOTICE )
                                if "http://github.com/" in url:
                                    new_name = self.set_github_skin( skin_name )
                                    if new_name: skin_name = new_name
                                xbmc.log( "[SCRIPT: %s] Skin installed - [%s, %s]" % ( __script__, skins_path, skin_name ), xbmc.LOGNOTICE )
                            else:
                                xbmcgui.Dialog().ok( GET_LOCALIZED_STRING( 32200 ), GET_LOCALIZED_STRING( 32210 ), GET_LOCALIZED_STRING( 32220 ) % xbmc.getFreeMem(), GET_LOCALIZED_STRING( 32230 ) % ( filesize * 1.5 )  )
                self.save_dir = dpath
        except:
            print_exc()

    def onAction( self, action ):
        if action in ( 9, 10 ):
            self.close()

    def set_github_skin( self, skin_name ):
        new_name = ""
        try:
            last = sorted( glob.glob( os.path.join( skins_path, "*" ) ), key=lambda s: os.path.getmtime( s ), reverse=True )
            last = ( last or [ "" ] )[ 0 ]
            if last and os.path.exists( last ):
                if not os.path.exists( os.path.join( skins_path, skin_name ) ):
                    base = skin_name
                else:
                    base = os.path.basename( last )
                    base = "-".join( base.split( "-" )[ 1:-1 ] ) or base
                while True:
                    new_name = ""
                    keyboard = xbmc.Keyboard( base, GET_LOCALIZED_STRING( 32120 ) )
                    keyboard.doModal()
                    if keyboard.isConfirmed():
                        new_name = keyboard.getText()
                        fpath = os.path.join( skins_path, new_name )
                        if ( new_name != os.path.basename( last ) ) and not os.path.exists( fpath ):
                            os.rename( last, fpath )
                            xbmc.log( "[SCRIPT: %s] set_github_skin::name: [%s for %s]" % ( __script__, last, fpath ), xbmc.LOGNOTICE )
                            break
                        new_name = ""
                    else:
                        xbmc.log( "[SCRIPT: %s] set_github_skin::name::canceled!" % ( __script__ ), xbmc.LOGNOTICE )
                        break
                if not new_name:
                    new_name = base
        except:
            print_exc()
            new_name = skin_name
        return new_name



if  __name__ == "__main__":
    current_skin, force_fallback = getUserSkin()
    w = nightly( "nightly.xml", CWD, current_skin, force_fallback )
    w.doModal()
    del w