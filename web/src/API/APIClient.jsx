
class APIClient {
    _instance = null; 
    constructor(base_url) {  
      if(APIClient._instance){
        return APIClient._instance;
      }
      APIClient.instance = this;
      this.base_url = base_url
      this.max_num_fetch = 1;
      this.delayBetweenRetries = 1000;
    }
    
    async response_handling(response){
      const contentLength = response.headers.get('Content-Length');
      if (contentLength && parseInt(contentLength, 10) > 0) {
          const body = await response.json();
          const data = body['body'];
          if (response.ok) {
            
            if ('data' in data) {
              return data['data'];            
            } else if ('message' in data) {
              return data['message'];
            } 

          }else{
            if ('error' in data) {
              return data['error'];            
            } else if ('message' in data) {
              return data['message'];
            } 
          }
      } else{
        if (response.ok) {
          return true;
      }else{
          return false;
      }
    }  
    }


    async _request(method,endpoint, body = null) {
      const url = `${this.base_url}${endpoint}`;
      console.info(`${method} - ${url}`);
      const requestOptions = {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
      };
      if (body !== null) {
        requestOptions.body = JSON.stringify(body);
      }
    

    for (let index = 0; index < this.max_num_fetch; index++) {
        try {
          const response = await fetch(url, requestOptions);
          return await this.response_handling(response);

        } catch (error) {
          console.error(`Retry attempt ${index + 1} failed with error:`, error);
          if (index + 1 === this.max_num_fetch){
            throw error;
          }
        }      
      await new Promise(resolve => setTimeout(resolve, this.delayBetweenRetries));
    }

    }

    async fetchModelOptions(){
      const endpoint = "/m"
      const method = "GET"
      const data = await this._request(method,endpoint)
      return data;
    }

    async fetchChats() {
      const endpoint = "/c"
      const method = "GET"
      const data = await this._request(method,endpoint)
      return data;
    }

    async getModelsData(){
      const endpoint = "/m"
      const method = "GET"
      const data = await this._request(method,endpoint)
      return data;
    }

    async getChats() {
      const endpoint = "/c"
      const method = "GET"
      const data = await this._request(method,endpoint)
      return data;
    }

    async converse(chat,prompt,model_name){
      const chat_id = chat.id
      if (!chat_id){
        return await this.createNewChat(prompt,model_name)
      }else{
        return await this.updateChat(chat_id,prompt,model_name)
      }
    }

    async createNewChat(prompt,model_name){
      const endpoint = "/c"
      const method = "POST"
      const body = {
        "prompt":prompt,
        "model_name":model_name
      }
      const data = await this._request(method,endpoint,body)
      return data;
    }

    async updateChat(chat_id,prompt,model_name){
      const endpoint = `/c/${chat_id}`
      const method = "PUT"
      const body = {
        "prompt":prompt,
        "model_name":model_name
      }
      const data = await this._request(method,endpoint,body);
      return data;
    }

    async getChat(chat_id){
      const endpoint = `/c/${chat_id}`
      const method = "GET"
      const data = await this._request(method,endpoint);
      return data;
    }

    async deleteChat(chat_id){
      const endpoint = `/c/${chat_id}`
      const method = "DELETE"
      const data = await this._request(method,endpoint);
      return data;
    }


}

const client = (function() {
  let host = "http://localhost"
  let port = 3001
  let base_url = `${host}:${port}`;
  if (!process.env.NODE_ENV || process.env.NODE_ENV === 'development') {
    // proxy
    // base_url = ""
  } else {
    
  }
  
  
  const api_client = new APIClient(base_url);
  return api_client;
})();


export default client;