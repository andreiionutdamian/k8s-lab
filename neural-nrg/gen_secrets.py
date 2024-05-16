import os
import base64
import argparse
from pathlib import Path

def load_env_file(env_file_path):
  """
  Load the .env file and parse key-value pairs.
  
  Parameters
  ----------
  env_file_path : str
    Path to the .env file.

  Returns
  -------
  dict
    Dictionary containing key-value pairs from the .env file.
  """
  env_vars = {}
  with open(env_file_path, 'r') as file:
    for line in file:
      if line.strip() and not line.startswith('#'):
        key, value = line.strip().split('=', 1)
        env_vars[key] = value
  return env_vars

def create_k8s_secret_yaml(secret_name, env_vars, namespace='default'):
  """
  Create a Kubernetes secret manifest in YAML format.

  Parameters
  ----------
  secret_name : str
    Name of the Kubernetes secret.
  env_vars : dict
    Dictionary containing key-value pairs to be included in the secret.
  namespace : str, optional
    Namespace for the Kubernetes secret, default is 'default'.

  Returns
  -------
  str
    Kubernetes secret manifest in YAML format.
  """
  yaml_template = """apiVersion: v1
kind: Secret
metadata:
  name: {secret_name}
  namespace: {namespace}
type: Opaque
data:
"""
  encoded_env_vars = {k: base64.b64encode(v.encode()).decode() for k, v in env_vars.items()}
  yaml_data = "\n".join([f"  {k}: {v}" for k, v in encoded_env_vars.items()])
  
  return yaml_template.format(secret_name=secret_name, namespace=namespace) + yaml_data

def save_to_file(content, file_path):
  """
  Save the content to a specified file.

  Parameters
  ----------
  content : str
    Content to be saved.
  file_path : str
    Path to the file where the content will be saved.
  """
  with open(file_path, 'w') as file:
    file.write(content)

def main():
  parser = argparse.ArgumentParser(description='Generate Kubernetes secret manifest from .env file')
  parser.add_argument('--env-file', type=str, default='.env', help='Path to the .env file (default: .env in current folder)')
  parser.add_argument('--secret-name', type=str, default='ne-secrets', help='Name of the Kubernetes secret')
  parser.add_argument('--namespace', type=str, default='ne', help='Namespace for the Kubernetes secret (default: default)')
  parser.add_argument('--output', type=str, default='secrets.yaml', help='Output file path for the secret manifest (default: secret.yaml in current folder)')
  
  args = parser.parse_args()

  env_file_path = Path(args.env_file)
  if not env_file_path.is_file():
    print(f"Error: .env file not found at {env_file_path}")
    return
  
  env_vars = load_env_file(env_file_path)
  k8s_secret_yaml = create_k8s_secret_yaml(args.secret_name, env_vars, args.namespace)
  
  output_file_path = Path(args.output)
  save_to_file(k8s_secret_yaml, output_file_path)
  print(f"Kubernetes secret manifest saved to {output_file_path}")

if __name__ == "__main__":
  main()
