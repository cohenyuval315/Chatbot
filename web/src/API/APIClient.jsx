
class APIClient {
    _instance = null; 
    constructor(base_url) {  
      if(APIClient._instance){
        return APIClient._instance;
      }
      APIClient.instance = this;
      this.base_url = base_url
    }
    
    async _request(method,endpoint, body = null) {
      const url = `${this.base_url}${endpoint}`;
      console.info(`${method} - ${url}`);
      const requestOptions = {
        method: method,
        headers: {
          // mode: 'no-cors',
          'Content-Type': 'application/json',
        },
      };
      if (body !== null) {
        requestOptions.body = JSON.stringify(body);
      }
    
      try {
        const response = await fetch(url, requestOptions);
        const data = await response.json();
        if (response.ok) {
          if (response.statusCode !== 200){
            
          }else{
            
          }
          return data; 
        } else {
          console.error(`Request failed with status ${response.status}: ${data.message}`);
          throw new Error(data.message || 'An error occurred during the request.');
        }
      } catch (error) {
        console.log(error)
        console.error(error.message);
        throw error;
      }
    }

    async fetchChats() {
      const endpoint = "/c"
      const method = "GET"
      const data = await this._request(method,endpoint)
      return data;
    }

    async converse(chat,prompt){
      const chat_id = chat.id
      if (!chat_id){
        return await this.createNewChat(prompt)
      }else{
        return await this.updateChat(chat_id,prompt)
      }
    }

    async createNewChat(prompt){
      const endpoint = "/c"
      const method = "POST"
      const body = {
        "prompt":prompt
      }
      const data = await this._request(method,endpoint,body)
      return data;
    }

    async updateChat(chat_id,prompt){
      const endpoint = `/c/${chat_id}`
      const method = "PUT"
      const body = {
        "prompt":prompt
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