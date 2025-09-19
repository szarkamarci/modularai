import mlflow.pyfunc
from mlflow.tracking
import MlflowClient
from mlflow.models.signature
import infer_signature
from mlflow.deployments
import get_deploy_client

def log_model(name : str = 'model', 
             python_model : mlflow.pyfunc.PythonModel = None, 
             #registered_model_name : str = None, 
             input_example : pd.DataFrame = None, 
             signature : mlflow.models.signature.ModelSignature = None): 
             
    with mlflow.start_run() as run: 
        logged_model_info = mlflow.pyfunc.log_model(
            name = name, 
            python_model = python_model, 
            input_example = input_example, 
            signature = signature, 
            #registered_model_name = model_name
        ) 
        
        #model_uri = f"runs:/{run.info.run_id}/model" 
        
    return logged_model_info 
    
    
def register_model(model_uri : str, registered_model_name : str): 
    registered_model_info = mlflow.register_model( 
        model_uri = model_uri, 
        name = registered_model_name ) 
        
    return registered_model_info 
    
    
def deploy_model(endpoint_name : str, 
                deploy_config : dict = None): 
                
    client = get_deploy_client('databricks') 
    
    endpoint = client.create_endpoint( 
        name = endpoint_name, 
        config = deploy_config)
        
    return endpoint
    
def run_mono_deployment(**kwargs):

    name = kwargs.get("name", "model")
    python_model = kwargs.get("python_model", None) 
    
    if python_model == None: 
        raise Exception("'python_model' is required") 
        
    input_example = kwargs.get("input_example", pd.DataFrame()) 
    if input_example.empty: 
        raise Exception("'input_example' is required")
    
    registered_model_name = kwargs.get("registered_model_name", None)
    if registered_model_name == None: 
        raise Exception("'registered_model_name' is required") 
    
    endpoint_name = kwargs.get("endpoint_name", None) 
    if endpoint_name == None: 
        raise Exception("'endpoint_name' is required") 
    
    deploy_config = kwargs.get("deploy_config", None) 
    if deploy_config == None: 
        raise Exception("'deploy_config' is required") 
        
    try: 
        signature = infer_signature(input_example, python_model.predict(input_example)) 
    except Exception as e:
        raise Exception (f"Failed to infer signature: {e}")
        
    logged_model_info = log_model(name = name, 
                                 python_model = python_model,
                                 input_example = input_example,
                                 signature = signature) 
    
    registered_model_info = register_model(model_uri = logged_model_info.model_uri, 
                                          registered_model_name = registered_model_name) 
    
    if "entity_version" in deploy_config['served_entities'][0]: 
        deploy_config['served_entities'][0]['entity_version'] = registered_model_info.version 
    else: deploy_config['served_entities'][0].update({"entity_version": registered_model_info.version}) 
    
    endpoint = deploy_model(endpoint_name = endpoint_name, 
                            deploy_config = deploy_config) 
                                        
    return endpoint