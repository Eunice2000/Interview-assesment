import os
import boto3
import pytest
import requests

class TestCRUDApi:
    
    @pytest.fixture()
    def api_gateway_url(self):
        """Get the API Gateway URL from Cloudformation Stack outputs"""
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        
        if stack_name is None:
            raise ValueError('Please set AWS_SAM_STACK_NAME environment variable')
        
        client = boto3.client("cloudformation")
        
        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(f"Cannot find stack {stack_name}") from e
        
        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        
        # Look for ApiGatewayUrl output (not HelloWorldApi)
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "ApiGatewayUrl"]
        
        if not api_outputs:
            raise KeyError(f"ApiGatewayUrl not found in stack {stack_name}")
        
        return api_outputs[0]["OutputValue"]
    
    def test_create_item(self, api_gateway_url):
        """Test creating an item"""
        url = f"{api_gateway_url}items"
        payload = {
            "name": "Test Item",
            "description": "Test description"
        }
        
        response = requests.post(url, json=payload)
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "id" in data, "Response should contain item ID"
        
        # Store ID for other tests
        self.item_id = data["id"]
    
    def test_list_items(self, api_gateway_url):
        """Test listing items"""
        url = f"{api_gateway_url}items"
        response = requests.get(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
    
    def test_get_item(self, api_gateway_url):
        """Test getting a specific item"""
        # First create an item to get
        create_url = f"{api_gateway_url}items"
        payload = {"name": "Get Test", "description": "For get test"}
        create_response = requests.post(create_url, json=payload)
        
        if create_response.status_code in [200, 201]:
            item_id = create_response.json()["id"]
            
            # Now get it
            get_url = f"{api_gateway_url}items/{item_id}"
            response = requests.get(get_url)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data["id"] == item_id, f"Expected ID {item_id}, got {data.get('id')}"
    
    def test_update_item(self, api_gateway_url):
        """Test updating an item"""
        # First create an item to update
        create_url = f"{api_gateway_url}items"
        payload = {"name": "Update Test", "description": "For update test"}
        create_response = requests.post(create_url, json=payload)
        
        if create_response.status_code in [200, 201]:
            item_id = create_response.json()["id"]
            
            # Update it
            update_url = f"{api_gateway_url}items/{item_id}"
            update_payload = {"name": "Updated Name", "description": "Updated description"}
            response = requests.put(update_url, json=update_payload)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_delete_item(self, api_gateway_url):
        """Test deleting an item"""
        # First create an item to delete
        create_url = f"{api_gateway_url}items"
        payload = {"name": "Delete Test", "description": "For delete test"}
        create_response = requests.post(create_url, json=payload)
        
        if create_response.status_code in [200, 201]:
            item_id = create_response.json()["id"]
            
            # Delete it
            delete_url = f"{api_gateway_url}items/{item_id}"
            response = requests.delete(delete_url)
            
            assert response.status_code in [200, 204], f"Expected 200/204, got {response.status_code}"
