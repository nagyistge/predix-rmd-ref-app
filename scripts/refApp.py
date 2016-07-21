import sys
import traceback
import time
import os
import subprocess
import fileinput

statementStatus  = subprocess.call('git submodule update --init --remote predix-scripts ', shell=True)
pwd=os.getcwd()
sys.path.insert(0, pwd)
print(sys.path)
sys.path.insert(0, pwd+'/predix-scripts/python')
print(sys.path)
from predix import *

#####################################################################################################
############################### main methods ###############################
#####################################################################################################
def updateGitModules(config):
	print("CurrentDir " + os.getcwd())
	if 'git@' in open('.gitmodules').read():
		config.updateGitModules='true'
		f1 = open('.gitmodules', 'r')
		f2 = open('.gitmodules.script', 'w')
		for line in f1:
			print(line)
			line = line.replace(':', '/')
			print(line)
			line = line.replace('git@', "https://")
			print(line)
			f2.write(line)
		f1.close()
		f2.close()
		shutil.copy(".gitmodules", ".gitmodules.bak")
		shutil.copy(".gitmodules.script", ".gitmodules")


def restoreGitModules(config):
	if ( os.path.isfile(".gitmodules.bak") ):
		print("restoring .gitmodules")
		shutil.copy(".gitmodules.bak", ".gitmodules")

def validate(config):
	try:
		config.current='validate'
		if not os.path.isfile(config.mvnsettings):
			msg = "File " + config.mvnsettings + " does not exist, please see setup instructions before continuing."
			raise ValueError(msg)
	except:
		print traceback.print_exc()
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			validate(config)
		else :
			raise

def deployReferenceAppDelete(config):
	try:
		if ( config.deleteAppsAndServices == "y" ):
			print("****************** Installing deployReferenceAppDelete ******************")
			config.current='deployReferenceAppDelete'
			# Deleting existing Applications and Services
			unbind(config.predixbootAppName,config.rmdUaaName)
			unbind(config.predixbootAppName,config.rmdAcsName)
			unbind(config.predixbootAppName,config.rmdPredixAssetName)
			unbind(config.predixbootAppName,config.rmdPredixTimeseriesName)
			deleteExistingApplication(config.predixbootAppName)

			unbind(config.fdhAppName, config.rmdPredixAssetName)
			unbind(config.fdhAppName, config.rmdPredixTimeseriesName)
			deleteExistingApplication(config.fdhAppName)

			unbind(config.dataSeedAppName,config.rmdUaaName)
			unbind(config.dataSeedAppName,config.rmdAcsName)
			unbind(config.dataSeedAppName,config.rmdPredixAssetName)
			deleteExistingApplication(config.dataSeedAppName)

			unbind(config.dataSourceAppName,config.rmdUaaName)
			unbind(config.dataSourceAppName,config.rmdAcsName)
			unbind(config.dataSourceAppName,config.rmdPredixAssetName)
			unbind(config.dataSourceAppName,config.rmdPredixTimeseriesName)
			deleteExistingApplication(config.dataSourceAppName)

			deleteExistingApplication(config.websocketAppName)

			unbind(config.dataIngestionAppName,config.rmdUaaName)
			deleteExistingApplication(config.dataIngestionAppName)

			deleteExistingApplication(config.machineSimulatorAppName)

			unbind(config.dataIngestionAppName,config.rmdUaaName)
			unbind(config.dataIngestionAppName,config.rmdPredixAssetName)
			unbind(config.dataIngestionAppName,config.rmdPredixTimeseriesName)
			unbind(config.dataIngestionAppName,config.rmdRedis)
			deleteExistingApplication(config.uiAppName)

			deleteExistingService(config.rmdUaaName)
			deleteExistingService(config.rmdAcsName)
			deleteExistingService(config.rmdPredixAssetName)
			deleteExistingService(config.rmdPredixTimeseriesName)
			deleteExistingService(config.rmdPostgres)
			deleteExistingService(config.rmdRedis)

			config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			time.sleep(10)  # Delay
			deployReferenceAppDelete(config)
		else :
			raise
	return statementStatus

def buildPredixSDKs(config):
	try:
		config.current='buildPredixSDKs'
		print("Fast install = " + config.fastinstall)

		if config.pullsubmodules == 'y':
			print("CurrentDir " + os.getcwd())
			statementStatus  = subprocess.call('git submodule update --init --remote predix-sdks', shell=True)
			print("CurrentDir " + os.getcwd())
			print("ChangeDir = " + config.predixSDKs)
			os.chdir(config.predixSDKs)
			try :
				updateGitModules(config)
				checkoutSubmodules()
			finally:
				restoreGitModules(config)
			print("ChangeDir = ..")
			os.chdir("..")
			print("Build using maven setting : "+config.mvnsettings +" Maven Repo : "+config.mavenRepo)
		if config.fastinstall != 'y' :
			print("Compiling code...")
			if config.mavenRepo != "":
				os.removedirs(config.mavenRepo)
				#statementStatus  = subprocess.call("rm -rf "+config.mavenRepo, shell=True)
				if config.mvnsettings == "":
					os.chdir(config.predixSDKs)
				 	statementStatus  = subprocess.call("mvn clean package -Dmaven.repo.local="+config.mavenRepo, shell=True)
					os.chdir("..")
				else:
					os.chdir(config.predixSDKs)
					statementStatus  = subprocess.call("mvn clean package -s ../"+config.mvnsettings+" -Dmaven.repo.local="+config.mavenRepo, shell=True)
					os.chdir("..")
			else:
				print("mvnSettings=" + config.mvnsettings)
				if config.mvnsettings == "":
					os.chdir(config.predixSDKs)
				 	statementStatus  = subprocess.call("mvn clean package", shell=True)
					os.chdir("..")
				else:
					os.chdir(config.predixSDKs)
				 	statementStatus  = subprocess.call("mvn clean package -s ../"+ config.mvnsettings, shell=True)
					os.chdir("..")
		 	if statementStatus != 0:
				print("Maven build failed.")
				sys.exit(1);
		config.retryCount=0
	except:
		print traceback.print_exc()
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			buildPredixSDKs(config)
		else :
			raise

def buildReferenceApp(config):
	try:
		config.current='buildReferenceApp'
		print("Fast install = " + config.fastinstall)
		if config.pullsubmodules == 'y':
			checkoutSubmodules()
			print("Build using maven setting : "+config.mvnsettings +" Maven Repo : "+config.mavenRepo)
		if config.fastinstall != 'y' :
			print("Compiling code...")
			if config.mavenRepo != "":
				os.removedirs(config.mavenRepo)
				#statementStatus  = subprocess.call("rm -rf "+config.mavenRepo, shell=True)
				if config.mvnsettings == "":
					statementStatus  = subprocess.call("mvn clean package -Dmaven.repo.local="+config.mavenRepo, shell=True)
				else:
					statementStatus  = subprocess.call("mvn clean package -s "+config.mvnsettings+" -Dmaven.repo.local="+config.mavenRepo, shell=True)
			else:
				if config.mvnsettings == "":
				 	statementStatus  = subprocess.call("mvn clean package", shell=True)
				else:
				 	statementStatus  = subprocess.call("mvn clean package -s "+config.mvnsettings, shell=True)
		 	if statementStatus != 0:
				print("Maven build failed.")
				sys.exit(1);
		config.retryCount=0
	except:
		print traceback.print_exc()
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			buildReferenceApp(config)
		else :
			raise

def deployAndBindUAAToPredixBoot(config):
	try:
		os.chdir(config.predixbootRepoName)
		cfPush(config.predixbootAppName, 'cf push '+config.predixbootAppName+' -f ' + 'manifest.yml')
		statementStatus  = subprocess.call("cf bs "+config.predixbootAppName +" " + config.rmdUaaName , shell=True)
		if statementStatus == 1 :
				sys.exit("Error binding a uaa service instance to boot ")

		#statementStatus  = subprocess.call("cf restage "+config.predixbootAppName, shell=True)
		#if statementStatus == 1 :
		#		sys.exit("Error restaging a uaa service instance to boot")
	finally:
		os.chdir("..")

def deployReferenceAppCreateUAA(config):
	try :
		print("****************** Running deployReferenceAppCreateUAA ******************")
		config.current='deployReferenceAppCreateUAA'
		# these two are modified by some other functions.
		getAuthorities(config)
		createPredixUAASecurityService(config)

		#Bind to Predix Boot
		deployAndBindUAAToPredixBoot(config)
		getPredixUAAConfigfromVcaps(config)

		#Create Client Id and Users
		createClientIdAndAddUser(config)
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateUAA(config)
		else :
			raise

def deployReferenceAppCreateACS(config):
	try :
		print("****************** Running deployReferenceAppCreateACS ******************")
		config.current='deployReferenceAppCreateACS'
		# acs integration
		getPredixUAAConfigfromVcaps(config)
		createBindPredixACSService(config,config.rmdAcsName)
		getPredixACSConfigfromVcaps(config)

		print("****************** ACS configured As ******************")
		print ("\n ACS_URI = " + config.ACS_URI + "\n "+config.acsPredixZoneHeaderName+"= " +config.acsPredixZoneHeaderValue)
		print (" ACS zone "+config.acsOauthScope)
		print("****************** ***************** ******************")

		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateACS(config)
		else :
			raise

def updateClientAuthoritiesAssetAndTimeseries(config):
	getClientAuthoritiesforAssetAndTimeSeriesService(config)

def deployReferenceAppCreateAssetAndTimeseries(config):
	try:
		print("****************** Running deployReferenceAppCreateAssetAndTimeseries ******************")
		config.current='deployReferenceAppCreateAssetAndTimeseries'

		# create a Asset Service
		print("****************** Predix Asset Timeseries ******************")
		createAsssetInstance(config,config.rmdPredixAssetName,config.predixAssetService)

		# create a Timeseries
		createTimeSeriesInstance(config,config.rmdPredixTimeseriesName,config.predixTimeSeriesService)

		bindService(config.predixbootAppName,config.rmdPredixAssetName)
		bindService(config.predixbootAppName,config.rmdPredixTimeseriesName)

		getVcapJsonForPredixBoot(config)
		getAssetURLandZone(config)
		getTimeseriesURLandZone(config)


		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateAssetAndTimeseries(config)
		else :
			raise

def deployReferenceAppAddAuthorities(config):
	try:
		print("****************** Running deployReferenceAppAddAuthorities ******************")
		config.current='deployReferenceAppAddAuthorities'
		getPredixUAAConfigfromVcaps(config)
		getAuthorities(config)
		updateClientAuthoritiesACS(config)
		updateClientAuthoritiesAssetAndTimeseries(config)
		updateClientIdAuthorities(config)

		updateUserACS(config)
		updateUAAUserGroups(config, config.timeSeriesQueryScopes+","+config.timeSeriesInjestScopes+","+config.assetScopes+","+config.acsOauthScope)

		# setting up ACS policy and Subject
		createRefAppACSPolicyAndSubject(config, config.acsPredixZoneHeaderValue)

		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppAddAuthorities(config)
		else :
			raise

def getDataseedUrl(config):
	if not hasattr(config,'DATA_SEED_URL') :
		cfTarget= subprocess.check_output(["cf", "app",config.dataSeedAppName])
		print (cfTarget)
		config.DATA_SEED_URL="https://"+cfTarget.split('urls:')[1].strip().split('last uploaded:')[0].strip()
		print ('dataSeedAppName URL '+config.DATA_SEED_URL)

def uploadFileToDataseed(url, data, files):
    httpProxy=os.environ.get('http_proxy')
    if httpProxy is not None:
		if "http" not in httpProxy:
			raise ValueError("http_proxy env var does not start with http:, using IP addresses is not recommended and is not supported by this script")

		print("Proxy =" + httpProxy)
		proxyHostPort=httpProxy.split("http://")[1]
		proxyHost=proxyHostPort.split(":")[0]
		proxyPort=proxyHostPort.split(":")[1]
		proxyPort1=proxyPort.split("/")[0]
		print("Proxyhost =" + proxyHost)
		print("Proxyport =" + proxyPort1)
		connection = HTTPSConnection (proxyHost, proxyPort1)
		print("URL to tunnel into =" + url.split("https://")[1])
		connection.set_tunnel(url.split("https://")[1])
		connection.set_debuglevel(3)
		connection.request ('POST', url + "/uploadAssetData",
                        *encode_multipart_data (data, files))
    else:
    	connection = HTTPSConnection (url.split("https://")[1])
	connection.set_debuglevel(3)
    	connection.request ('POST', "/uploadAssetData",
                        *encode_multipart_data (data, files))
    response = connection.getresponse ()
    print ('Code: %s %s', response.status, response.reason)
    #print ('response = %s', response.read ())
    return response.read()

def deployReferenceAppCreateDataseed(config):
	try:
		print("****************** Running deployReferenceAppCreateDataseed ******************")
		config.current='deployReferenceAppCreateDataseed'
		getPredixUAAConfigfromVcaps(config)
		getPredixACSConfigfromVcaps(config)
		dataSeedRepoName = "data-seed-service"
		configureManifest(config, dataSeedRepoName)
		pushProject(config,config.dataSeedAppName, 'cf push '+config.dataSeedAppName+' -f '+dataSeedRepoName+'/manifest.yml',dataSeedRepoName, checkIfExists="false")

		getDataseedUrl(config)

		data = {'username' : config.rmdAdmin1,
        		'password' : config.rmdAdmin1Pass}

		files = {'file' : './data-seed-service/src/main/resources/rmdapp/AssetData.xls'}

		#calling data loading on dataseedURl
		output= uploadFileToDataseed(config.DATA_SEED_URL, data, files)
		print ("output=" + output)
		if ( not output == "You successfully uploaded file!" ) :
			sys.exit('unable to upload Asset Data in deployReferenceAppCreateDataseed, output=' + output)

		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateDataseed(config)
		else :
			raise

def getRMDDatasourceUrl(config):
	if not hasattr(config,'RMD_DATASOURCE_URL') :
		cfTarget= subprocess.check_output(["cf", "app",config.dataSourceAppName])
		print (cfTarget)
		config.RMD_DATASOURCE_URL="https://"+cfTarget.split('urls:')[1].strip().split('last uploaded:')[0].strip()
		print ('Data dataSourceAppName URL '+config.RMD_DATASOURCE_URL)

def deployReferenceAppCreateDatasource(config):
	try:
		print("****************** Running deployReferenceAppCreateDatasource ******************")
		config.current='deployReferenceAppCreateDatasource'
		getPredixUAAConfigfromVcaps(config)
		dataSourceRepoName = "rmd-datasource"
		configureManifest(config, dataSourceRepoName)
		pushProject(config, config.dataSourceAppName, 'cf push '+config.dataSourceAppName+' -f '+dataSourceRepoName+'/manifest.yml',dataSourceRepoName, checkIfExists="false")

		getRMDDatasourceUrl(config)


		#postgresJsonrequest = "cf cs "+config.predixPostgres+" "+config.predixPostgresPlan+" "+config.rmdPostgres
		#print ("Creating Postgres cmd "+postgresJsonrequest)
		#statementStatus  = subprocess.call(postgresJsonrequest, shell=True)

		#httpDatariverRepoName = "predix-http-datariver"
		#checkoutDeploytHttpRiver(httpDatariverRepoName,"",httpDataRiverAppName)

		#https://github.build.ge.com/adoption/predix-websocket-server.git
		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			time.sleep(10)  # Delay
			deployReferenceAppCreateDatasource(config)
		else :
			raise

def getWebsocketAppInfo(config):
	if not hasattr(config,'WEB_SOCKET_HOST') :
		print("****************** Running getWebsocketAppInfo ******************")
		cfTarget= subprocess.check_output(["cf", "app",config.websocketAppName])
		print (cfTarget)
		config.WEB_SOCKET_HOST=cfTarget.split('urls:')[1].strip().split('last uploaded:')[0].strip()
		print ('WS ingestion URL '+config.WEB_SOCKET_HOST)
		config.LIVE_DATA_WS_URL="wss://"+config.WEB_SOCKET_HOST
		print ('LIVE_DATA_WS_URL '+config.LIVE_DATA_WS_URL)

def deployReferenceAppCreateWebsocketServer(config):
	try:
		config.current='deployReferenceAppCreateWebsocketServer'
		getPredixUAAConfigfromVcaps(config)
		websocketServerRepoName = "predix-websocket-server"
		configureManifest(config, websocketServerRepoName)
		pushProject(config, config.websocketAppName, 'cf push '+config.websocketAppName+' -f '+websocketServerRepoName+'/manifest.yml',websocketServerRepoName, checkIfExists="false")

		getWebsocketAppInfo(config)
		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateWebsocketServer(config)
		else :
			raise


def deployReferenceAppCreateDataIngestion(config):
	try:
		print("****************** Running deployReferenceAppCreateDataIngestion ******************")
		config.current='deployReferenceAppCreateDataIngestion'
		getPredixUAAConfigfromVcaps(config)
		getWebsocketAppInfo(config)
		dataIngestionRepoName = "dataingestion-service"
		configureManifest(config, dataIngestionRepoName)
		pushProject(config, config.dataIngestionAppName, 'cf push '+config.dataIngestionAppName+' -f '+dataIngestionRepoName+'/manifest.yml',dataIngestionRepoName, checkIfExists="false")


		cfTarget= subprocess.check_output(["cf", "app",config.dataIngestionAppName])
		print (cfTarget)
		config.DATA_INGESTION_URL="https://"+cfTarget.split('urls:')[1].strip().split('last uploaded:')[0].strip()
		print ('Data Ingestion URL '+config.DATA_INGESTION_URL)
		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateDataIngestion(config)
		else :
			raise

def deployReferenceAppCreateMachineSimulator(config):
	try:
		print("****************** Running deployReferenceAppCreateMachineSimulator ******************")
		config.current='deployReferenceAppCreateMachineSimulator'
		getPredixUAAConfigfromVcaps(config)
		machineSimulatorRepoName = "machinedata-simulator"
		configureManifest(config, machineSimulatorRepoName)
		pushProject(config, config.machineSimulatorAppName, 'cf push '+config.machineSimulatorAppName+' -f '+machineSimulatorRepoName+'/manifest.yml',machineSimulatorRepoName, checkIfExists="false")
		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateMachineSimulator(config)
		else :
			raise

def deployReferenceAppCreateUI(config):
	try:
		print("****************** Running deployReferenceAppCreateUI ******************")
		config.current='deployReferenceAppCreateUI'
		print("findRedisService")
		findRedisService(config)
		getPredixUAAConfigfromVcaps(config)
		getRMDDatasourceUrl(config)
		getWebsocketAppInfo(config)

		getVcapJsonForPredixBoot(config)
		getAssetURLandZone(config)
		getTimeseriesURLandZone(config)

		print("*********Create redis********************")
		redisJsonrequest = "cf cs "+config.predixRedis+" "+config.predixRedisPlan+" "+config.rmdRedis
		print ("Creating Redis cmd "+redisJsonrequest)
		statementStatus = subprocess.call(redisJsonrequest, shell=True)

		print("*********Deploying UI application********************")
		uiRepoName = "rmd-ref-app-ui"
		checkoutAndDeployUI(config, uiRepoName, config.uiAppName)

		print("********* DONE deploying UI application ********************")
		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppCreateUI(config)
		else :
			raise

def checkoutAndDeployUI(config, repoName,appDeploymentName):
	try:
		print ("deploying "+repoName)
		os.chdir(repoName)
		print ("Changed directory to "+os.getcwd())
		statementStatus  = subprocess.check_output("npm install --production",shell=True)
		statementStatus  = subprocess.check_output("bower install --config.strict-ssl=false", shell=True)
		statementStatus  = subprocess.check_output("grunt dist --fast", shell=True)
		configureManifest(config, ".")
		configureConnectServer(config,"./tasks/options/")
		cfPush(appDeploymentName, 'cf push '+appDeploymentName)
	except:
		print ( 'having trouble with the github username pass?  try downloading the dependencies manually by running "npm install", "bower install", and "grunt dist" from the rmd-ref-app-ui dir.  Then go back to the root dir run "python scripts/installRefApp.py --continueFrom deployReferenceAppCreateUI"')
		print ()
		raise
	finally:
		os.chdir("..")

def configureManifest(config, manifestLocation):
	# create a backup
	if os.path.isfile(manifestLocation + "/manifest.yml"):
		shutil.copy(manifestLocation+"/manifest.yml", manifestLocation+"/manifest.yml.bak")
	# copy template as manifest
	shutil.copy(manifestLocation+"/manifest.yml.template", manifestLocation+"/manifest.yml")
	s = open(manifestLocation+"/manifest.yml").read()
	s = s.replace('${assetService}', config.rmdPredixAssetName)
	s = s.replace('${uaaService}', config.rmdUaaName)
	s = s.replace('${acsService}', config.rmdAcsName)
	s = s.replace('${oauthRestHost}', config.UAA_URI.replace('https://',''))
	s = s.replace('${clientId}', config.rmdAppClientId)
	s = s.replace('${secret}', config.rmdAppSecret)
	if hasattr(config,'ACS_URI') :
		s = s.replace('${acsURI}', config.ACS_URI)
	s = s.replace('${timeSeriesService}', config.rmdPredixTimeseriesName)
	s = s.replace('${acssubdomain}', 'rmdsubdomain')
	s = s.replace('${postgresqService}', config.rmdPostgres)
	if hasattr(config,'DATA_INGESTION_URL') :
		s = s.replace('${dataIngestionUrl}', config.DATA_INGESTION_URL)
	s = s.replace('${sessionService}', config.rmdRedis)
	s = s.replace('${UAA_SERVER_URL}', config.UAA_URI)
	if hasattr(config,'ASSET_URI') :
		s = s.replace('${ASSET_URL}', config.ASSET_URI)
		s = s.replace('${ASSET_ZONE}', config.ASSET_ZONE)
	if hasattr(config,'TS_URI') :
		s = s.replace('${TS_URL}', config.TS_URI.split('/api/')[0])
		s = s.replace('${TS_ZONE}', config.TS_ZONE)
	s = s.replace('${ENCODED_CLIENTID}', base64.b64encode(config.rmdAppClientId+":"+config.rmdAppSecret))
	if hasattr(config,'RMD_DATASOURCE_URL') :
		s = s.replace('${RMD_DATASOURCE_URL}', config.RMD_DATASOURCE_URL)
	if hasattr(config,'WEB_SOCKET_HOST') :
		s = s.replace('${WEB_SOCKET_HOST}', config.WEB_SOCKET_HOST)
		s = s.replace('${LIVE_DATA_WS_URL}', config.LIVE_DATA_WS_URL)
	f = open(manifestLocation+"/manifest.yml", 'w')
	f.write(s)
	f.close()
	with open(manifestLocation+'/manifest.yml', 'r') as fin:
		print (fin.read())

def configureConnectServer(config, fileLocation):
	# create a backup
	if os.path.isfile(fileLocation + "/connect.js"):
		shutil.copy(fileLocation+"/connect.js", fileLocation+"/connect.js.bak")
	# copy template as manifest
	shutil.copy(fileLocation+"/connect.js.template", fileLocation+"/connect.js")
	s = open(fileLocation+"/connect.js").read()
	s = s.replace('${clientId}', config.rmdAppClientId)
	s = s.replace('${secret}', config.rmdAppSecret)
	s = s.replace('${UAA_SERVER_URL}', config.UAA_URI)
	s = s.replace('${ASSET_URL}', config.ASSET_URI)
	s = s.replace('${ASSET_ZONE}', config.ASSET_ZONE)
	s = s.replace('${TS_URL}', config.TS_URI.split('/api/')[0])
	s = s.replace('${TS_ZONE}', config.TS_ZONE)
	s = s.replace('${ENCODED_CLIENTID}', base64.b64encode(config.rmdAppClientId+":"+config.rmdAppSecret))
	s = s.replace('${RMD_DATASOURCE_URL}', config.RMD_DATASOURCE_URL)
	s = s.replace('${LIVE_DATA_WS_URL}', config.LIVE_DATA_WS_URL)
	f = open(fileLocation+"/connect.js", 'w')
	f.write(s)
	f.close()
	# with open(fileLocation+'/connect.js', 'r') as fin:
	# 	print (fin.read())

def deployReferenceAppFinalPrep(config):
	try:
		print("****************** Running deployReferenceAppFinalPrep ******************")
		config.current='deployReferenceAppFinalPrep'

		getPredixUAAConfigfromVcaps(config)

		stopSimulatorRequest = "cf stop "+config.machineSimulatorAppName
		statementStatus  = subprocess.call(stopSimulatorRequest, shell=True)

		#restageApplication(config.predixbootAppName)
		#print("***********************Restage Predix Boot Completed**********************")
		config.retryCount=0
	except:
		print(traceback.print_exc())
		print()
		print ('Exception when running ' + config.current + '.  Retrying')
		config.retryCount = config.retryCount + 1
		if config.retryCount <= 1 :
			deployReferenceAppFinalPrep(config)
		else :
			raise

def sanityChecks(config):
	config.current='sanityChecks'
	# Sanity checks:
	jsonrequest = "cf apps | grep "+config.instanceAppender
	statementStatus  = subprocess.call(jsonrequest, shell=True)

	jsonrequest = "cf s | grep "+ config.instanceAppender
	statementStatus  = subprocess.call(jsonrequest, shell=True)

	cfTarget= subprocess.check_output(["cf", "app",config.uiAppName])
	print (cfTarget)
	config.uiUrl="https://"+cfTarget.split('urls:')[1].strip().split('last uploaded:')[0].strip()

	getDataseedUrl(config)
	getPredixUAAConfigfromVcaps(config)
	getVcapJsonForPredixBoot(config)
	getAssetURLandZone(config)
	getTimeseriesURLandZone(config)
	getPredixACSConfigfromVcaps(config)
	getDataseedUrl(config)
	getRMDDatasourceUrl(config)
	getWebsocketAppInfo(config)

	print ('uaaAdmin= ' + config.uaaAdminSecret)
	print ('clientId= ' + config.rmdAppClientId)
	print ('clientSecret= ' + config.rmdAppSecret)
	print ('rmdUser= ' + config.rmdUser1)
	print ('rmdUserPass= ' + config.rmdUser1Pass)
	print ('rmdAdmin= ' + config.rmdAdmin1)
	print ('rmdAdminPass= ' + config.rmdAdmin1Pass)
	print ('client basic auth= ' + base64.b64encode(config.rmdAppClientId+":"+config.rmdAppSecret))
	print ('UAA_SERVER_URL= ' + config.UAA_URI)
	print ('ASSET_URL= ' + config.ASSET_URI)
	print ('ASSET_ZONE= ' + config.ASSET_ZONE)
	print ('TS_URI= ' + config.TS_URI)
	print ('TS_ZONE= ' + config.TS_ZONE)
	print ('ACS_URI= ' + config.ACS_URI)
	print ('ACS_Zone_Id= ' + config.acsPredixZoneHeaderValue)
	print ('DATASOURCE= ' + config.RMD_DATASOURCE_URL)
	print ('WEBSOCKET_URL= ' + config.LIVE_DATA_WS_URL)
