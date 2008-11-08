# -*- coding: cp1252 -*-

"""
Le Blog d'Alain Carraz� Video HTML parser with GUI by Temhil (temhil@gmail.com)
 
18-10-08 Version 1.0-Dev05 by Temhil
    - Created info window for videos
    - Fixed regex after changes on the website
    - Major update of the UI
    - Replaced regex by beautiful soup for the XML processing

26-04-08 Version Beta1 by Temhil
    - Creation

Les droits des diffusions et des images utilis�es sont exclusivement
r�serv�s � Canal+ 

"""

############################################################################
version     = '1.1-Dev01'
author      = 'Temhil'
############################################################################

############################################################################
# import  
############################################################################
from string import *
import sys, os.path
import re
import urllib, urllib2, cookielib
import ConfigParser
import traceback
from time import gmtime, strptime, strftime

try:
    import xbmcgui, xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'


############################################################################
# emulator
############################################################################
try: 
    Emulating = xbmcgui.Emulating
except: 
    Emulating = False


############################################################################
# Get current working directory and update internal vars with it  
############################################################################

# Set paths
ROOTDIR = xbmc.translatePath(os.getcwd().replace( ";", "" )) # Create a path with valid format

IMAGEDIR    = os.path.join(ROOTDIR, "images")
CACHEDIR    = os.path.join(ROOTDIR, "cache")
#DOWNLOADDIR = os.path.join(ROOTDIR, "download")
LIBDIR      = os.path.join(ROOTDIR, "lib")

# List of directories to check at startup
dirCheckList   = (CACHEDIR,) #Tuple - Singleton (Note Extra ,)

# Adding to sys PATH lib path
sys.path.append(LIBDIR)

# Import lib
from BeautifulSoup import BeautifulStoneSoup #librairie de traitement XML


############################################################################
# Get actioncodes from keymap.xml
############################################################################

ACTION_MOVE_LEFT                 = 1    
ACTION_MOVE_RIGHT                = 2
ACTION_MOVE_UP                   = 3
ACTION_MOVE_DOWN                 = 4
ACTION_PAGE_UP                   = 5
ACTION_PAGE_DOWN                 = 6
ACTION_SELECT_ITEM               = 7
ACTION_HIGHLIGHT_ITEM            = 8
ACTION_PARENT_DIR                = 9
ACTION_PREVIOUS_MENU             = 10
ACTION_SHOW_INFO                 = 11

ACTION_PAUSE                     = 12
ACTION_STOP	                     = 13
ACTION_NEXT_ITEM                 = 14
ACTION_PREV_ITEM                 = 15

#############################################################################
# autoscaling values
#############################################################################

HDTV_1080i      = 0 #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p       = 1 #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3   = 2 #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9  = 3 #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3        = 4 #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9       = 5 #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3         = 6 #(720x576, 4:3, pixels are 128:117)
PAL_16x9        = 7 #(720x576, 16:9, pixels are 512:351)
PAL60_4x3       = 8 #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9      = 9 #(720x480, 16:9, pixels are 5760:4739)

#############################################################################
# Player values
#############################################################################
PLAYER_AUTO         = 0 # xbmc.PLAYER_CORE_AUTO
PLAYER_DVDPLAYER    = 1 # xbmc.PLAYER_CORE_DVDPLAYER
PLAYER_MPLAYER      = 2 # xbmc.PLAYER_CORE_MPLAYER

# Create a tuple matching to the value above
playerSelect = (xbmc.PLAYER_CORE_AUTO,
                xbmc.PLAYER_CORE_DVDPLAYER,
                xbmc.PLAYER_CORE_MPLAYER)
#############################################################################
# Control alignment
#############################################################################
xbfont_left         = 0x00000000
xbfont_right        = 0x00000001
xbfont_center_x     = 0x00000002
xbfont_center_y     = 0x00000004
xbfont_truncated    = 0x00000008

#############################################################################
# URLs
#############################################################################

bacBasePageURL = "http://alaincarraze.blog.canal-plus.com/"
xmlBasepageURL = "http://www.canalplus.fr/flash/xml/module/embed-video-player/embed-video-player.php?video_id="

# Set Headers
txdata = None
txheaders = {	
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7'
}


def downloadJPG(source, destination):
    """
    Source MyCine (thanks!)
    Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
    Source is downloaded only if target doesn't already exist
    """
    print("downloadJPG with source = " + source)
    print("downloadJPG with destination = " + destination)
    if os.path.exists(destination):
        print("downloadJPG destination already exist")
        pass
    else:
        try:
            print("downloadJPG destination doesn't exist, try to retrieve")
            loc = urllib.URLopener()
            loc.retrieve(source, destination)
        except Exception, e:
            print("Exception while source retrieving")
            print(e)
            pass


class WebPage:
    """
    
    Load a remote Web page (html,xml) and provides source code
    
    """
    def __init__(self, url, txData, txHearder):
        """
        - Init of WebPage
        - Load the Web page at the specific URL
          and copy the source code in self.Source
        """
        try:
            # CookieJar objects support the iterator protocol for iterating over contained Cookie objects.
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            req = urllib2.Request(url, txData, txHearder)
            u = opener.open(req)
            headers = u.info()
            self.Source = u.read()

        except Exception, e:
            print("Exception in WebPage init for URL: " + url)
            print(e)
            
            # pass the Exception
            raise e

class bacVideoDescriptWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video description webpage
    
    """
    def GetVideoDescription(self):
        """
        Extract video description from the AC blog collection webpage
        Parameters:
            - [out] Video description
        """
        videoDate       = ""
        videoTitle      = ""
        videoDesciption = ""
        reVideo     = re.compile(r'<h2 class="date"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">  <p>(?P<videoDescription>.+?)<br />', re.DOTALL) 
        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            videoDate       = unicode(i.group("videoDate"),"utf-8").encode("cp1252")
            videoTitle      = unicode(i.group("videoTitle"),"utf-8").encode("cp1252")
            videoDesciption = unicode(i.group("videoDescription"),"utf-8").encode("cp1252")
        
        return videoDate,videoTitle,videoDesciption

    def GetVideoCommentsList(self):
        """
        Extract video comments from the AC blog collection webpage
        Parameters:
            - [out] Video comments
        """
        commentIDList           = []
        commentDescriptionList  = []
        commentAuthorList       = []
        commentDateList         = [] 
        reVideo = re.compile(r'<a id=\"(?P<commentID>[a-zA-Z0-9]+?)\"></a> <p>(?P<commentDescription>.+?)</p> <p class="posted"> Ecrit par : (<a.+?>(?P<commentAuthor1>.+?)</a>|(?P<commentAuthor2>.+?)) \| (?P<commentDate>.+?) </p>', re.DOTALL) 
        
        
        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            commentIDList.append(unicode(i.group("commentID"),"utf-8").encode("cp1252"))
            
            commentDesRaw       = unicode(i.group("commentDescription"),"utf-8").encode("cp1252")
            commentDescription  = re.sub(r"<.*?>", r"", commentDesRaw)
            commentDescriptionList.append(commentDescription)
            
            commentAuthor = i.group("commentAuthor1")
            if commentAuthor == None:
                commentAuthor = i.group("commentAuthor2")
            commentAuthorList.append(unicode(commentAuthor,"utf-8").encode("cp1252"))
            
            commentDateList.append(unicode(i.group("commentDate"),"utf-8").encode("cp1252"))
         
        print commentIDList
        print commentDescriptionList
        print commentAuthorList
        print commentDateList
        
        return commentIDList,commentDescriptionList,commentAuthorList,commentDateList

class bacVideoListWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video list webpage
    which include list of video to watch) and provides source code
    
    """
    def GetVideoList(self, dataObj):
        """
        Extract data about video files from the AC blog collection webpage
        Parameters:
            - [out] dataObj: Data object (bacCollectionData) where data 
              extracted from the Webpage  will be appended 
        """
        #reVideo = re.compile(r'<h2\ class=\"date\"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div id="playercontent(?P<videoID>[0-9]+?)">.*?\|.*?<a href="http://alaincarraze\.blog\.canal-plus\.com/(?P<videoDescriptURL>.+?)\">Lien permanent</a>', re.DOTALL) 
        reVideo = re.compile(r"""<h2\ class=\"date\"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div id="playercontent(?P<videoID>[0-9]+?)">.*?<a href="http://alaincarraze\.blog\.canal-plus\.com/(?P<videoDescriptURL>[a-zA-Z0-9+-=._/*(),@'$:;&!?]+?html)\">Lien permanent</a>""", re.DOTALL) 

        ##TODO Exception on nothing found !!!!!!!!!!!!!!!!!!!!!!!!

        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            dataObj.videoIDList.append(i.group("videoID"))
            dataObj.videoDateList.append(unicode(i.group("videoDate"),"utf-8").encode("cp1252"))
            dataObj.videotitleList.append(unicode(i.group("videoTitle"),"utf-8").encode("cp1252"))
            dataObj.videoPageList.append(i.group("videoDescriptURL"))

    def GetCategoryList(self):
        """
        Extract data about categories from the AC blog collection webpage
        Parameters:
            - [out] List :list of categories
        """
        reStripCat      = re.compile(r'<div\ id=\"box-categories\".*?<ul>(.*?)</ul>', re.DOTALL) 
        reCategories    = re.compile(r'<li><a href="http://alaincarraze\.blog\.canal-plus\.com/(?P<catURL>.+?)\">(?P<catName>.+?)</a></li>', re.DOTALL) 
        
        stripHtmlCategoriesList = reStripCat.findall(self.Source)
        stripHtmlCategories     = ""
        if len(stripHtmlCategoriesList) > 0:
            stripHtmlCategories = stripHtmlCategoriesList[0]
        categoryListName = []
        categoryListURL = []
        categoryListName.append("Accueil")
        categoryListURL.append("")
        
        for i in reCategories.finditer(stripHtmlCategories):
            # Copy each item found in a list
            categoryListName.append(unicode(i.group("catName"),"utf-8").encode("cp1252"))
            categoryListURL.append(i.group("catURL"))
        return categoryListName,categoryListURL
        
class bacVideoXML(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video XML page
    (which include video URL to watch) and provides source code
    
    """
    def __init__(self, url, txData, txHearder):
        """
        - Init of WebPage
        - Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__(self, url, txData, txHearder)

        print("Loading XML file: " + url)
        self.videoHQFileURL = ""
        self.videoLQFileURL = ""
        self.videoImageURL  = ""

        # Extract video File Name from the AC blog webpage
        soup = BeautifulStoneSoup(self.Source)
        self.videoHQFileURL = soup.find('hi').string.encode("utf-8")
        self.videoLQFileURL = soup.find('low').string.encode("utf-8")
        self.videoImageURL = soup.find("image").find('url').string.encode("utf-8")
    
    def GetVideoURL(self,videoQuality):
        """
        Return URL of video files extracted from the AC blog webpage
        """
        if videoQuality == "HQ":
            return self.videoHQFileURL
        elif videoQuality == "LQ":
            return self.videoLQFileURL
        else:
            return self.videoHQFileURL

    def GetVideoImageURL(self):
        """
        Return Video Image URL of video files extracted from the AC Blog webpage
        """
        return (self.videoImageURL)


class bacCollectionData:
    """
    
    Data Warehouse for datas extracted from collection web page(s) 
    (one or more depending on number of pages)
    
    """
    def __init__(self):
        """
        Init of bacCollectionData
        """
        self.dataLoaded	       = False # define if data has been extracted from a collection webpage
        self.numberOfPages     = 0     # number of webpage for a collection
        self.videoPageList     = []    # video page URL
        self.videotitleList    = []    # Title of a video    
        self.videoImageList    = []    # Video Image URL 
        self.videoIDList       = []    # Video ID
        self.videoDateList     = []    # Video Date

        print("bacCollectionData init DONE")

    def reset(self):
        """
        Reset of bacCollectionData attributes
        """
        self.dataLoaded	       = False
        self.numberOfPages     = 0
        self.videoPageList     = []
        self.videotitleList    = []
        self.videoImageList    = []
        self.videoIDList       = []
        self.videoDateList     = [] 
        print("bacCollectionData RESET DONE")
    
    def getNumberofItem(self):
        """
        Return the total number of item (videos) found for the collection
        """
        #print("NumberofItem for = " + str(self.videoPageList))
        #return len(self.videoPageList)
        return len(self.videoIDList)

class SelectCollectionWebpage:
    """
    
    Allow to select a Collection Webpage to process (i.e by vote, by date ...)
    
    """
    def __init__(self, pagebaseUrl, nameSelecList, urlSelectList):
        self.selectedMenu	      = 0
        self.baseUrl		      = pagebaseUrl
        self.selectionNameList	  = nameSelecList
        self.selectionURLList	  = urlSelectList
        self.selectCollecData	  = []
        self.menulen		      = len(nameSelecList)

        #TODO: check len(nameSelecList) == len(urlSelectList)

        # Filling selectCollecData
        for i in range(self.menulen):
            self.selectCollecData.append(bacCollectionData())

class configCtrl:
    """
    
    Controler of configuration
    
    """
    def __init__(self):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = False
        self.defaultPlayer = PLAYER_AUTO
        self.video_quality = "HQ"
        self.delCache      = True
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(ROOTDIR,"blogAC.cfg"))
            
            # Check sections exist
            if (self.config.has_section("system") == False):
                self.config.add_section("system")
                self.is_conf_valid = False
                
            # - Read config from file and correct it if necessary
            if (self.config.has_option("system", "player") == False):
                self.config.set("system", "player", self.defaultPlayer)
                self.is_conf_valid = False
            else:
                self.defaultPlayer = int(self.config.get("system", "player"))
            if (self.config.has_option("system", "video_quality") == False):
                self.config.set("system", "video_quality", self.video_quality)
                self.is_conf_valid = False
            else:
                self.video_quality = self.config.get("system", "video_quality")
            if (self.config.has_option("system", "cleancache") == False):
                self.config.set("system", "cleancache", self.delCache)
                self.is_conf_valid = False
            else:
                self.delCache = self.config.getboolean("system", "cleancache")
            if (self.is_conf_valid == False):
                # Update file
                print "CFG file format wasn't valid: correcting ..."
                cfgfile=open(os.path.join(ROOTDIR,"blogAC.cfg"), 'w+')
                try:
                    self.config.write(cfgfile)
                    self.is_conf_valid = True
                except Exception, e:
                    print("Exception during setPassword")
                    print(str(e))
                    print (str(sys.exc_info()[0]))
                    traceback.print_exc()
                cfgfile.close()
        except Exception, e:
            print("Exception while loading configuration file " + "blogAC.cfg")
            print(str(e))
        
    def setDefaultPlayer(self,playerType):
        """
        set DefaultPlayerparameter locally and in .cfg file
        """
        self.defaultPlayer = playerType
        
        # Set player parameter
        self.config.set("system", "player", playerType)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blogAC.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setDefaultPlayer")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getDefaultPlayer(self):
        """
        return the player currently used
        """
        return self.defaultPlayer
        
    def setVideoQuality(self,videoQuality):
        """
        set video quality parameter locally and in .cfg file
        """
        self.video_quality = videoQuality
        
        # Set player parameter
        self.config.set("system", "video_quality", videoQuality)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blogAC.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setVideoQuality")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getVideoQuality(self):
        """
        return the video quality currently used
        """
        return self.video_quality

    def setCleanCache(self,cleanCacheStatus):
        """
        set clean cache status locally and in .cfg file
        @param cleanCacheStatus: clean cache status - define cache directory will be cleaned or not on exit
        """
        self.delCache = cleanCacheStatus
        
        # Set cachepages parameter
        self.config.set("system", "cleancache", self.delCache)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blogAC.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setCleanCache")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getCleanCache(self):
        """
        return current clean cache status - define cache directory will be cleaned or not on exit
        """
        return self.delCache


class fileMgr:
    """
    
    File manager
    
    """
    #TODO: Create superclass, inherit and overwrite init
    def __init__(self,checkList):
        for i in range(len(checkList)):
            self.verifrep(checkList[i]) 

    def verifrep(self, folder):
        """
        Source MyCine (thanks!)
        Check a folder exists and make it if necessary
        """
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print("verifrep Impossible to find the directory - trying to create the directory: " + folder)
                os.makedirs(folder)
        except Exception, e:
            print("Exception while creating folder " + folder)
            print(str(e))
            
    def listDirFiles(self, path):
        """
        List the files of a directory
        @param path:
        """
        dirList=os.listdir(path)
        return dirList
        
    def deleteFile(self, filename):
        """
        Delete a file form download directory
        @param filename:
        """
        os.remove(filename)
        
    def delFiles(self,folder):
        """
        From Joox
        Deletes all files in a given folder and sub-folders.
        Note that the sub-folders itself are not deleted.
        Parameters : folder=path to local folder
        """
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
    
    def  extract(self,archive,targetDir):
        """
        Extract an archive in targetDir
        """
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(archive,targetDir) )

class SettingsWindow(xbmcgui.WindowDialog):
    """
    
    This window display settings
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

    def setWindow(self,configManager):
        self.configManager   = configManager
        self.strListMaxSize  = 50
        self.playerMenuList  = ["Auto","DVD Player","MPlayer"]
        self.qualityMenuList = ["HQ","LQ"]
        self.cleanCacheList  = ["Activ�","D�sactiv�"]
        
        # Background image
        self.addControl(xbmcgui.ControlImage(138,120,445,335, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Title label:
        self.strlist = xbmcgui.ControlLabel(138, 125, 445, 30, 'Options', 'special13',alignment=6)
        self.addControl(self.strlist)

        # Get settings
        self.defaultPlayer  = self.configManager.getDefaultPlayer()
        self.videoQuality   = self.configManager.getVideoQuality()
        self.cleanCache     = self.configManager.getCleanCache()
        
        
        # item Control List
        self.strDefaultPlayerTitle   = "Player vid�o: "
        self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
        self.strVideoQualityTitle    = "Qualit� vid�o: "
        self.strVideoQualityContent  = str(self.videoQuality)
        self.strCleanCacheTitle      = "Nettoyage auto du cache: "
        if self.cleanCache:
            self.strCleanCacheContent = self.cleanCacheList[0] #Activ�
        else:
            self.strCleanCacheContent = self.cleanCacheList[1] #D�sactiv�
            
        self.settingsListData = [self.strDefaultPlayerTitle + self.strDefaultPlayerContent, self.strVideoQualityTitle + self.strVideoQualityContent, self.strCleanCacheTitle + self.strCleanCacheContent]
        self.settingsList = xbmcgui.ControlList(158, 170, 300 , 400,'font14', buttonTexture = os.path.join(IMAGEDIR,"list-black-nofocus.png"), buttonFocusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), itemTextXOffset=-10, itemHeight=30)
        self.addControl(self.settingsList)
            
        # OK button:
        self.buttonOK = xbmcgui.ControlButton(478, 170, 80, 30, "OK",font='font12', focusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-black-nofocus.png"), alignment=6)
        self.addControl(self.buttonOK)
        
        self.settingsList.controlLeft(self.buttonOK)
        self.settingsList.controlRight(self.buttonOK)
        self.buttonOK.controlLeft(self.settingsList)
        self.buttonOK.controlRight(self.settingsList)

        for labelItem in self.settingsListData:
            displayListItem = (xbmcgui.ListItem(label = labelItem))
            # Add list item to the ControlList
            self.settingsList.addItem(displayListItem)
        self.setFocus(self.settingsList)
        
        # show this menu and wait until it's closed
        self.doModal()

    #TODO: Create a general update function???
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            
    def onControl(self, control):
        if control == self.settingsList:
            selectedIndex = self.settingsList.getSelectedPosition()
            print("selectedIndex = " + str(selectedIndex))
            if selectedIndex == 0:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner le Player d�sir�', self.playerMenuList)
                self.configManager.setDefaultPlayer(chosenIndex)
                self.defaultPlayer           = chosenIndex
                self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strDefaultPlayerTitle + self.strDefaultPlayerContent)
            elif selectedIndex == 1:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la Qualit� vid�o d�sir�e', self.qualityMenuList)
                self.configManager.setVideoQuality(self.qualityMenuList[chosenIndex])
                self.videoQuality            = self.qualityMenuList[chosenIndex]
                self.strVideoQualityContent  = str(self.videoQuality)
                self.settingsList.getListItem(selectedIndex).setLabel(self.strVideoQualityTitle + self.strVideoQualityContent)
                
            elif selectedIndex == 2:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la gestion du cache d�sir�e', self.cleanCacheList)
                if chosenIndex == 0:
                    self.configManager.setCleanCache(True)
                    self.cleanCache           = True
                    self.strCleanCacheContent = self.cleanCacheList[0] #Activ�
                else:
                    self.configManager.setCleanCache(False)
                    self.cleanCache           = False
                    self.strCleanCacheContent = self.cleanCacheList[1] #D�sactiv�
                self.settingsList.getListItem(selectedIndex).setLabel(self.strCleanCacheTitle + self.strCleanCacheContent)
            else:
                print "SettingsWindow - onControl : Invalid control list index"

        elif control == self.buttonOK:
            self.close()

class AboutWindow(xbmcgui.WindowDialog):
    """
    
    About Window
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))
        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, "Le Blog d'Alain Carraz�",'special13')
        self.addControl(self.strTitle)
        self.strVersion = xbmcgui.ControlLabel(130, 140, 350, 30, "Version: " + version)
        self.addControl(self.strVersion)
        self.strAuthor = xbmcgui.ControlLabel(130, 170, 350, 30, "Auteur: "+ author)
        self.addControl(self.strAuthor)        
        self.strDesTitle = xbmcgui.ControlLabel(130, 200, 350, 30, "Description: ")
        self.addControl(self.strDesTitle)        
        strContent = """Ce script vous permet de vous connecter sur le Blog d'Alain Carraz� 
(http://alaincarraze.blog.canal-plus.com) et de visionner les videos
du blog ainsi que d'en lire leur description.
"""
        self.strDesContent = xbmcgui.ControlLabel(130, 220, 490, 100, strContent, "font12", textColor='0xFFD3D3D3')
        self.addControl(self.strDesContent)

        self.strACTitle = xbmcgui.ControlLabel(130, 290, 350, 30, "A propos d'Alain Carraz�: ")
        self.addControl(self.strACTitle) 
               
        strAboutAC = """Depuis ses d�buts en 1979 en tant que collaborateur de 'Temps X', l'�mission de science-fiction, Alain CARRAZE � partag� ses passions pour le cin�ma fantastique, les comics et surtout les s�ries TV � travers des �missions comme 'Fantasy' ( dans le cadre des 'Enfants du Rock' ) et principalement la cultissime 'Destination S�ries', sur Canal Jimmy de 1992 � 2000 (pres de 225 �ditions) , avec aussi des �missions sp�ciales comme le 'Marathon Friends', 'La F�te � Jerry Seinfeld', les Emmy Awards ou la 'Nuit Star Trek'.
A travers des magazines, aussi, comme 'Esode, le magazine de la culture s�ries', des hors-s�ries pour Mad Movies ou 'Episodik'. A travers des livres, enfin, avec des ouvrages comme 'Le Prisonnier, chef d'oeuvre t�l�visionnaire', ou sur 'Chapeau Melon et Bottes de Cuir ', 'Mission: Impossible', 'Les Grandes S�ries' et, r�cemment, la mini-encyclopedie 'Les s�ries t�l�' dans la collection 'Toute les Cl�s '.
Il travaille sur des bonus de DVD ('Amicalement V�tre', 'Le Prisonnier', 'Twin Peaks'), chronique aussi les s�ries � la radio et dans un grand quinzomadaire de programmes t�l�... et maintenant en exclusivit� sur Canalplus.fr !
"""
        self.aboutACTextBox = xbmcgui.ControlTextBox(130, 310, 545-50, 145, font="font12", textColor='0xFFD3D3D3')
        self.addControl(self.aboutACTextBox)
        self.aboutACTextBox.setText(strAboutAC)
        self.aboutACTextBox.setVisible(True)
        self.setFocus(self.aboutACTextBox)
        
        strCopyRight = """Les droits des diffusions et des images utilis�es sont exclusivement r�serv�s
� Canal+"""
        self.strCopyRight = xbmcgui.ControlLabel(130, 465, 500, 20,strCopyRight, "font10",'0xFFFF0000')
        self.addControl(self.strCopyRight)
        
        self.doModal()
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            

class InfoWindow(xbmcgui.WindowDialog):
    """
    
    This window display informations about a video
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Set the Video Image at top-left position
        self.videoPicture = xbmcgui.ControlImage(130,120,214,160, os.path.join(IMAGEDIR,"noImageAvailable.jpg"))
        self.addControl(self.videoPicture)
        self.videoPicture.setVisible(True)

    def updateImage(self,path):
        """
        Update the image of the video in the window
        """
        self.videoPicture.setImage(path)

    def updateInfo(self,videoDate,videoTitle,videoDesciption):
        """
        Set and fill the information for a video
        """
        self.strDate = xbmcgui.ControlLabel(355, 120, 200, 30, videoDate,'special13')
        self.addControl(self.strDate)
        self.strTitle = xbmcgui.ControlLabel(355, 150, 270, 30, videoTitle,'special13')
        self.addControl(self.strTitle)
        self.descriptTextBox = xbmcgui.ControlTextBox(130, 290, 545-50, 245, font="font12", textColor='0xFFFFFFFF')
        self.addControl(self.descriptTextBox)
        self.descriptTextBox.setText(videoDesciption)
        self.descriptTextBox.setVisible(True)
        self.setFocus(self.descriptTextBox)
        

class MainWindow(xbmcgui.Window):
    """
    AC Blog main UI
    """
    def __init__(self):

        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        # Create a file manager and check directory
        self.fileMgr = fileMgr(dirCheckList)

        # Check conf file
        self.configManager = configCtrl()
        
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("Le Blog d'Alain Carraz�", "Creation de l'interface Graphique", "Veuillez patienter...")

        # Background image
        print ("Get Background image from : " + os.path.join(IMAGEDIR,"background.png"))
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
       
        # Set the Video logo at top-left position
        print ("Get Logo image from : " + os.path.join(IMAGEDIR,"logo.png"))
        self.user_logo = xbmcgui.ControlImage(550,25,130,97, os.path.join(IMAGEDIR, "portrait.jpg"))
        self.addControl(self.user_logo)
        self.user_logo.setVisible(True)

        # Extract categories from main webpage
        mainWebPage=bacVideoListWebPage(bacBasePageURL ,txdata,txheaders)
        self.bacNameSelectList,self.bacUrlSelectList = mainWebPage.GetCategoryList()
        
        # Create selectCollectionWebpage instance in order to display choice of video collection
        self.CollectionSelector = SelectCollectionWebpage(bacBasePageURL, self.bacNameSelectList, self.bacUrlSelectList)

        # Menu Control List
        menuItemsize   = 30
        menuItemNumber = len(self.bacNameSelectList)
        if menuItemNumber > 11:
            menuItemNumber = 11 # We don't want to go outise the screen if the number of categories is too big
        menuListSize   = menuItemsize * menuItemNumber
        menuListWidth = 175
        self.Menulist = xbmcgui.ControlList(25, 190, menuListWidth, menuListSize, space=0,font='font12', textColor='0xFF000000',itemTextXOffset=-5, buttonTexture = os.path.join(IMAGEDIR,"list-background.png"), buttonFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))

        # Videos Control List
        #self.list = xbmcgui.ControlList(207, 140, 393, 380, space=8, itemHeight=80, font='font12', textColor='0xFF000000',itemTextXOffset=0, buttonFocusTexture  = os.path.join(IMAGEDIR,"list-background.png"),imageWidth=107, imageHeight=80)
        self.list = xbmcgui.ControlList(207, 140, 473, 380, space=8, itemHeight=80, font='font12', textColor='0xFF000000',itemTextXOffset=0, buttonFocusTexture  = os.path.join(IMAGEDIR,"list-background.png"),imageWidth=107, imageHeight=80)

        # Title of the current page
        title =  "LE BLOG D'ALAIN CARRAZ�"
        self.strMainTitle = xbmcgui.ControlLabel(230, 40, 270, 20, title, 'special13','0xFF000000',alignment=6)

        # Current Cat�gories Title
        self.strButton = xbmcgui.ControlLabel(230, 80, 270, 20, self.CollectionSelector.selectionNameList[self.CollectionSelector.selectedMenu], 'special13','0xFF000000',alignment=6)

        # List label:
        self.strlist = xbmcgui.ControlLabel(250, 300, 260, 20, '', 'font12', '0xFFFF0000')

        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel(600, 530, 150, 20, '0 Vid�o', 'font12', '0xFFFF0000')

        # Version and author:
        self.strVersion = xbmcgui.ControlLabel(230, 58, 270, 20,"v" + version,'font10', '0xFFFF0000',alignment=6)


        self.addControl(self.list)
        self.addControl(self.Menulist)
        self.addControl(self.strButton)
        self.addControl(self.strlist)
        self.addControl(self.strMainTitle)
        self.addControl(self.strItemNb)
        self.addControl(self.strVersion)
          
        # Option button:
        self.buttonOption = xbmcgui.ControlButton(25, 190 + menuListSize - menuItemsize + 5, menuListWidth, 30, "Options",font='font12', textColor='0xFF000000', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-background.png"),textXOffset=15)
        self.addControl(self.buttonOption)

        # About button:
        self.buttonAbout = xbmcgui.ControlButton(25, 220 + menuListSize - menuItemsize + 5, menuListWidth, 30, "A propos",font='font12', textColor='0xFF000000', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-background.png"),textXOffset=15)
        self.addControl(self.buttonAbout)

        self.list.controlLeft(self.Menulist)
        self.Menulist.controlRight(self.list)
        self.Menulist.controlUp(self.buttonOption)
        self.Menulist.controlDown(self.buttonOption)
        self.buttonOption.controlRight(self.list)
        self.buttonOption.controlUp(self.Menulist)
        self.buttonOption.controlDown(self.buttonAbout)
        self.buttonAbout.controlRight(self.list)
        self.buttonAbout.controlUp(self.buttonOption)
        self.buttonAbout.controlDown(self.Menulist)

        # add items to the Menu list
        xbmcgui.lock()
        for name in self.CollectionSelector.selectionNameList:		 
            self.Menulist.addItem(xbmcgui.ListItem(label = name))
        xbmcgui.unlock()


        # Set Focus on Menulist
        self.setFocus(self.Menulist)

        # Close the Loading Window 
        dialogUI.close()
       
        # Update the list of video 
        
        self.updateControlList(self.CollectionSelector.selectedMenu)
        # Start to diplay the window before doModal call
        self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.updateIcons(self.CollectionSelector.selectedMenu)

    def updateData(self, menuSelectIndex):
        """
        Update Data objet for a specific index (menu) 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create("Le blog d'Alain Carraz�", "Chargement des informations", "Veuillez patienter...")

        # Load Main webpage of Blog d'Alain Carraz�
        myVideoListWebPage=bacVideoListWebPage((bacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex]),txdata,txheaders)
           
        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
        myVideoListWebPage.GetVideoList(self.CollectionSelector.selectCollecData[menuSelectIndex])
        myVideoListWebPage.GetCategoryList()
        
       
        # Update dataLoaded flag
        self.CollectionSelector.selectCollecData[menuSelectIndex].dataLoaded = True

        # Close the Loading Window 
        dialogLoading.close()

    def updateControlList(self, menuSelectIndex):
        """
        Update ControlList objet
        """
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create("Le Blog d'Alain Carraz�", "Chargement des images", "Veuillez patienter...")
        try:
          
            # Check is data have already been loaded for this collection
            if (self.CollectionSelector.selectCollecData[menuSelectIndex].dataLoaded == False):
                # Never been updated before, go and get the data
                self.updateData(menuSelectIndex)
            

            # Get and Update number of video at the bottom of the page        
            numberOfPictures = self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
            self.strItemNb.setLabel(str(numberOfPictures) + " Vid�os" ) 
                
            # Lock the UI in order to add pictures
            xbmcgui.lock()    

            # Clear all ListItems in this control list 
            self.list.reset()

            #for name in self.CollectionSelector.selectCollecData[menuSelectIndex].videotitleList:
            #	 index = self.CollectionSelector.selectCollecData[menuSelectIndex].videotitleList.index(name)		
            for date in self.CollectionSelector.selectCollecData[menuSelectIndex].videoDateList:
                index = self.CollectionSelector.selectCollecData[menuSelectIndex].videoDateList.index(date) 
               
                pic = CACHEDIR + self.CollectionSelector.selectCollecData[menuSelectIndex].videoIDList[index] + ".jpg"
                title = self.CollectionSelector.selectCollecData[menuSelectIndex].videotitleList[index]
                if not os.path.exists(pic):
                    # images not here use default
                    print("Image" + pic + "not found - use default image")
                    pic=os.path.join(IMAGEDIR,"noImageAvailable.jpg")
                    
                # Add in the List pictures
                self.list.addItem(xbmcgui.ListItem(label = date + "\n" + title, thumbnailImage = pic))
                
            if not self.CollectionSelector.selectCollecData[menuSelectIndex].videoIDList:
                self.strlist.setLabel("Il n'y a pas d'�missions disponibles")
            else:
                self.strlist.setLabel("")
                # Set focus on the list
                self.setFocus(self.list)

            # Go back on 1st button (even if overwritten later)
            self.setFocus(self.Menulist)
        
            # Unlock the UI 
            xbmcgui.unlock()

            dialogimg.close()
        except Exception, e:
            print("Exception")
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()

            dialogimg.update(100)

            # Unlock the UI 
            xbmcgui.unlock()
            dialogimg.close()
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Impossible de charger la liste des Video du �", "un probleme de connection ou �", "un changement sur le site distant")

    def updateIcons(self, menuSelectIndex):
        """
        Retrieve images and update list
        """
        # Now get the images:
        try:       
            for date in self.CollectionSelector.selectCollecData[menuSelectIndex].videoDateList:
                index = self.CollectionSelector.selectCollecData[menuSelectIndex].videoDateList.index(date) 
                # Load video XML file
                myVideoXMLPage = bacVideoXML(xmlBasepageURL + self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoIDList[index],txdata,txheaders)
        
                # Get the URL of the video picture
                videoimg = myVideoXMLPage.GetVideoImageURL()
    
                videoimgdest = os.path.join(CACHEDIR,self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoIDList[index] + ".jpg")
    
                #print("Try to Download : " + videoimg)
                #print("at : " + videoimgdest)
                if not os.path.exists(videoimgdest):
                    # Download the picture    
                    try:
                        downloadJPG(videoimg, videoimgdest)
                        #print("Downloaded: " + videoimgdest)
                        
                    except:
                        print("Exception on image download")
                        videoimgdest=os.path.join(IMAGEDIR,"noImageAvailable.jpg")
                # Display the picture
                if os.path.exists(videoimgdest):
                    self.list.getListItem(index).setThumbnailImage(videoimgdest)
        except Exception, e:
            print("Exception")
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()


    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            print('action received: previous')
            # Clean the cache is requested
            if self.configManager.getCleanCache() == True:
                print "Deleting cache"
                self.fileMgr.delFiles(CACHEDIR)
                
            self.close()

            
        if action == ACTION_SHOW_INFO:
            # Show the information for a video
            
            chosenIndex = self.list.getSelectedPosition()
     
            # Display Loading Window while we are loading the information from the website
            dialogVideo = xbmcgui.DialogProgress()
            dialogVideo.create("Blog d'Alain Carraz�", "Chargement des informations sur la vid�o", "Veuillez patienter...")
            try:	   
                # Load video XML file
                myVideoXMLPage = bacVideoXML(xmlBasepageURL + self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoIDList[chosenIndex],txdata,txheaders)
                dialogVideo.update(33)				    

                # Get the URL of the video picture and create path for local fiel
                videoimg = myVideoXMLPage.GetVideoImageURL()
                videoimgdest = os.path.join(CACHEDIR,self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoIDList[chosenIndex] + ".jpg")
                
                if not os.path.exists(videoimgdest):
                    # Download the picture    
                    try:
                        downloadJPG(videoimg, videoimgdest)
                    except Exception, e:
                        print("Exception on image download")
                        print(e)
                        print (str(sys.exc_info()[0]))
                        traceback.print_exc()
                        videoimgdest=os.path.join(IMAGEDIR,"noImageAvailable.jpg")
                dialogVideo.update(66)                    

                # Get video description page
                myVideoDescriptPage=bacVideoDescriptWebPage(bacBasePageURL + self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoPageList[chosenIndex],txdata,txheaders)
                myVideoDate,myVideoTitle,myVideoDesciption = myVideoDescriptPage.GetVideoDescription()
                
                #TODO: Add display of comments:
                #myVideoDescriptPage.GetVideoCommentsList()
                
                dialogVideo.update(100)
                dialogVideo.close()
                
                # Create winInfoVideo
                winInfoVideo = InfoWindow()
                # Update image and info and display
                winInfoVideo.updateInfo(myVideoDate,myVideoTitle,myVideoDesciption)
                winInfoVideo.updateImage(videoimgdest)
                winInfoVideo.doModal()   
                del winInfoVideo

            except Exception, e:
                print("Exception")
                print(e)
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
                dialogVideo.update(100)
                dialogVideo.close()
                dialogError = xbmcgui.Dialog()
                dialogError.ok("Erreur", "Impossible de charger les informations du �", "- un probleme de connection", "- un changement sur le site distant")

    
    def onControl(self, control):
        if control == self.Menulist:
            menuSelectedIndex = self.Menulist.getSelectedPosition()
            self.CollectionSelector.selectedMenu = menuSelectedIndex
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[menuSelectedIndex])
            self.updateControlList(menuSelectedIndex)
            self.setFocus(self.Menulist)
            self.updateIcons(menuSelectedIndex)

        elif control == self.buttonOption:
            winSettingsVideo = SettingsWindow()
            winSettingsVideo.setWindow(self.configManager) # include doModal call
            del winSettingsVideo
            
        elif control == self.buttonAbout:
            winAboutVideo = AboutWindow()
            del winAboutVideo

        elif control == self.list:
            chosenIndex = self.list.getSelectedPosition()
    
            # Display Loading Window while we are loading the information from the website
            dialogVideo = xbmcgui.DialogProgress()
            dialogVideo.create("Blog d'Alain Carraz�", "Chargement des informations sur la vid�o", "Veuillez patienter...")
            try:
                # Load video XML file
                myVideoXMLPage = bacVideoXML(xmlBasepageURL + self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoIDList[chosenIndex],txdata,txheaders)

                # Update Progress bar (half of the job is done)
                dialogVideo.update(50)
      
                # Get the URL of the video to play
                video2playURL= myVideoXMLPage.GetVideoURL(self.configManager.getVideoQuality())

                dialogVideo.update(100)
                dialogVideo.close()

            except Exception, e:
                print("Exception")
                print(e)
                dialogVideo.update(100)
                dialogVideo.close()
                dialogError = xbmcgui.Dialog()
                dialogError.ok("Erreur", "Impossible de charger les informations du �", "un probleme de connection ou �", "un changement sur le site distant")
  
  
            # Play the selected video
            print("Play the selected video: %s"%video2playURL)
            xbmc.Player(self.configManager.getDefaultPlayer()).play(video2playURL)



########
#
# Main
#
########

print("=============================================================================")
print("")
print("	    Le Blog d'Alain Carraz� " + version + " by "+ author +" HTML parser STARTS")
print("")
print("=============================================================================")

# Create main Window
bacgui = MainWindow()

# Display this window until close() is called
bacgui.doModal()

del bacgui

 

