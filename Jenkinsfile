@Library(['Jenkinslibs_generic_utils@trunk']) _

// ==================================================== Method Pointer Operators =================================================================================

to_native_separators = jenkins.&to_native_separators_of_slave   // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
printenv = jenkins.&printenv                                    // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
ensure_delete_workspace = jenkins.&ensure_delete_workspace      // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
sh_bat = jenkins.&sh_bat                                        // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
isUnixEnv = jenkins.&isUnixEnv                                  // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
zipDirectory = jenkins.&zipDirectory                            // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
extractZipArtifact = jenkins.&extractZipArtifact                // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy
mkdir = jenkins.&mkdir                                          // http://roa-dev/repos/projects/internal/jenkinslibs/generic_utils/trunk/vars/jenkins.groovy

// ======================================================= Global variables ====================================================================================

AGENT_LABEL_EXTRAS_WIN = "jenkins-extras-win"
AGENT_LABEL_EXTRAS_LNX = "jenkins-extras-lnx"

PRODUCT_VERSION = "v${env.BRANCH_NAME}".replace('/', '_') 
PRODUCT_VERSION = (PRODUCT_VERSION ==~ /^v[0-9]+(\.[0-9]+)*$/) ? PRODUCT_VERSION : 'devel' 

// ======================================================= Steps description ====================================================================================

/**
* venv location depends on platform
*/
def get_python_venv_root(){
    return isUnixEnv() ?  "${env.WORKSPACE}/.venv/bin" :"${env.WORKSPACE}\\.venv\\Scripts"
}

/**
* separator depends on platform 
*/
def append_in_variable(def var_value, def to_append){
    return "${to_append}${isUnixEnv() ? ":" : ";"}${var_value}"
}

/**
* Platform dir depends on platform
*/
def get_patform_dir(){
    return isUnixEnv() ? "lnx_x64" : "win64"
}

/**
* Generate workspace name with branche name
*/
def get_ws_name(){
    return (env.BRANCH_NAME.toLowerCase()).replace("/", "_")
}

/**
* xtreamcache unit tests
*/
def tests_step(def type){
    printenv()
    mkdir("tmp")
    mkdir("sources")

    extractZipArtifact(env.JOB_BASE_NAME, env.BUILD_NUMBER, 'sources.zip', 'sources')

    def python_exe = to_native_separators("${get_python_venv_root()}/python")
    def junit_results = to_native_separators("${env.WORKSPACE}/results.junit")

    sh_bat("python -m pip install virtualenv")
    sh_bat("python -m virtualenv .venv")
    dir("sources"){
        withPythonEnv(python_exe) {
            withEnv(["PATH=${append_in_variable(env.PATH, get_python_venv_root())}"]) {
                sh_bat "python -m pip install -r dist-requirements.txt"
                sh_bat "python -m pip install -r test-requirements.txt"
                sh_bat "python -m xmlrunner discover tests/${type} --output-file ${junit_results}"
            }
        }
    }
}


/**
* Checkout xtremcache sources
*
*/
def step_checkout_sources(){
    printenv()

    // Checkout HMS sourcess
    dir('sources'){
        checkout(changelog: false, scm: scm)
    }
    
}


// ======================================================= Pipeline description =============================================================================

pipeline {
    agent {
        node {
            label AGENT_LABEL_EXTRAS_LNX
            customWorkspace "workspace/xrm_${get_ws_name()}_${env.BUILD_NUMBER}"
        }
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '300', artifactDaysToKeepStr: '2'))
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }
    stages {
        stage("Checkout") {
            agent {
                node {
                    label AGENT_LABEL_EXTRAS_LNX 
                    customWorkspace "workspace/xrm_${get_ws_name()}_sc_${env.BUILD_NUMBER}"
                }
            }
            steps {
                 script{
                    step_checkout_sources()
                }
            }
            post {
                success {
                    script{
                        zip(zipFile:'sources.zip', dir:'sources', exclude:'**/.git/**', archive:true)
                        ensure_delete_workspace()
                    }
                }
            }
        }
        stage("Tests") {
            parallel {
                stage("Windows") {
                    stages {
                        stage("Windows unit tests"){
                            agent {
                                node {
                                    label AGENT_LABEL_EXTRAS_WIN
                                    customWorkspace "workspace/xrm_${get_ws_name()}_ut_${env.BUILD_NUMBER}"
                                }
                            }
                            environment{
                                TMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TEMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TMPDIR = to_native_separators("${env.WORKSPACE}/tmp")
                            }
                            steps {
                                script{
                                    tests_step('unit')
                                }
                            }
                            post {
                                success {
                                    script{
                                        junit "*.junit"
                                        ensure_delete_workspace()
                                    }
                                }
                            }
                        }
                        stage("Windows integration tests"){
                            agent {
                                node {
                                    label AGENT_LABEL_EXTRAS_WIN
                                    customWorkspace "workspace/xrm_${get_ws_name()}_it_${env.BUILD_NUMBER}"
                                }
                            }
                            environment{
                                TMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TEMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TMPDIR = to_native_separators("${env.WORKSPACE}/tmp")
                            }
                            steps {
                                script{
                                    tests_step('integration')
                                }
                            }
                            post {
                                success {
                                    script{
                                        junit "*.junit"
                                        ensure_delete_workspace()
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Linux") {
                    stages {
                        stage("Linux unit tests"){
                            agent {
                                node {
                                    label AGENT_LABEL_EXTRAS_LNX
                                    customWorkspace "workspace/xrm_${get_ws_name()}_ut_${env.BUILD_NUMBER}"
                                }
                            }
                            environment{
                                TMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TEMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TMPDIR = to_native_separators("${env.WORKSPACE}/tmp")
                            }
                            steps {
                                script{
                                    tests_step('unit')
                                }
                            }
                            post {
                                success {
                                    script{
                                        junit "*.junit"
                                        ensure_delete_workspace()
                                    }
                                }
                            }
                        }
                        stage("Linux integration tests"){
                            agent {
                                node {
                                    label AGENT_LABEL_EXTRAS_LNX
                                    customWorkspace "workspace/xrm_${get_ws_name()}_it_${env.BUILD_NUMBER}"
                                }
                            }
                            environment{
                                TMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TEMP = to_native_separators("${env.WORKSPACE}/tmp")
                                TMPDIR = to_native_separators("${env.WORKSPACE}/tmp")
                            }
                            steps {
                                script{
                                    tests_step('integration')
                                }
                            }
                            post {
                                success {
                                    script{
                                        junit "*.junit"
                                        ensure_delete_workspace()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
