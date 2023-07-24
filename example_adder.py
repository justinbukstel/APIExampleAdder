import json
import argparse

def prompt_example_values(parameters):
    example_values = {}
    for parameter in parameters:
        parameter_name = parameter["name"]
        parameter_type = parameter["schema"]["type"]
        if "example" in parameter["schema"]:
            continue  # Skip parameters with existing example values
        method = parameter["method"]
        endpoint = parameter["endpoint"]
        example = input(f"Enter an example value for parameter '{parameter_name}' of type '{parameter_type}' for the '{method}' request in '{endpoint}': ")
        example_values[parameter_name] = example
    return example_values

def prompt_request_body_example_values(request_body_properties, method, endpoint):
    example_values = {}
    for prop_name, prop_data in request_body_properties.items():
        if "example" in prop_data:
            continue
        prop_type = prop_data["type"]
        example = input(f"Enter an example value for property '{prop_name}' of type '{prop_type}' in the request body for the '{method}' request in '{endpoint}': ")
        example_values[prop_name] = example
    return example_values

def add_example_values(openapi_spec, example_values):
    for path in openapi_spec["paths"]:
        for method in openapi_spec["paths"][path]:
            if "parameters" in openapi_spec["paths"][path][method]:
                for parameter in openapi_spec["paths"][path][method]["parameters"]:
                    parameter_name = parameter["name"]
                    if parameter_name in example_values:
                        parameter["schema"]["example"] = example_values[parameter_name]
                        parameter.pop("method", None)
                        parameter.pop("endpoint", None)

            if method in ["put", "post"] and "requestBody" in openapi_spec["paths"][path][method]:
                request_body_content = openapi_spec["paths"][path][method]["requestBody"]["content"]
                if "application/json" in request_body_content:
                    properties = request_body_content["application/json"]["schema"]["properties"]
                    for prop_name, prop_data in properties.items():
                        if "example" not in prop_data:
                            if prop_name in example_values:
                                prop_data["example"] = example_values[prop_name]

def write_openapi_spec(openapi_spec, filename):
    with open(filename, "w") as file:
        json.dump(openapi_spec, file, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Add example values to OpenAPI specification.")
    parser.add_argument("filepath", help="Path to the JSON OpenAPI specification file")
    args = parser.parse_args()

    # Read the OpenAPI specification file
    filename = args.filepath
    with open(filename, "r") as file:
        openapi_spec = json.load(file)

    # Identify parameters requiring example values
    parameters = []
    for path in openapi_spec["paths"]:
        for method in openapi_spec["paths"][path]:
            if "parameters" in openapi_spec["paths"][path][method]:
                for parameter in openapi_spec["paths"][path][method]["parameters"]:
                    parameter["method"] = method
                    parameter["endpoint"] = path
                    parameters.append(parameter)

    # Identify request body properties requiring example values
    request_body_example_values = {}
    if "paths" in openapi_spec:
        for path in openapi_spec["paths"]:
            for method in openapi_spec["paths"][path]:
                if method in ["put", "post"] and "requestBody" in openapi_spec["paths"][path][method]:
                    request_body_content = openapi_spec["paths"][path][method]["requestBody"]["content"]
                    if "application/json" in request_body_content:
                        properties = request_body_content["application/json"]["schema"]["properties"]
                        request_body_example_values = prompt_request_body_example_values(properties, method, path)

    # Prompt the user for example values for parameters
    example_values = prompt_example_values(parameters)

    if not example_values and not request_body_example_values:
        print("All parameters and request body properties already have example values. No further input needed.")
        return

    # Update the OpenAPI specification with example values for parameters and request body properties
    add_example_values(openapi_spec, example_values)
    add_example_values(openapi_spec, request_body_example_values)

    # Write the modified OpenAPI specification to a file
    updated_filename = "openapi_with_examples.json"
    write_openapi_spec(openapi_spec, updated_filename)
    print(f"Updated OpenAPI specification written to '{updated_filename}'.")

if __name__ == "__main__":
    main()


















