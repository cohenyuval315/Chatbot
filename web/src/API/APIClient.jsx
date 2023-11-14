import { v4 as uuid } from "uuid";

class APIClient {
    constructor() {  
        if (!APIClient.instance) {
            APIClient.instance = this;
            this.host = "localhost"
            this.port = 3001
            this.base_url = `${this.host}:${this.port}`;
        }
    }


    async fetchChats() {
      // get /c
      const path = "/c"
      const method = "GET"
      const url = this.base_url + path
      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
        }
      });
      const res = await response.json();
      if (res.statusCode !== 200){
        return []
      }else{
        return res.data
      }

        const chatData = [
            {
              "id":uuid(),
              "title":"hello",
              "log": [
                {
                  id:uuid(),
                  prompt:"text1(user)",
                  response:"text1(bot)",
                },
                {
                  id:uuid(),
                  prompt:"text2(user)",
                  response:"text2(bot)",
                }          
              ]
            },
            {
              "id":uuid(),
              "title":"hello2",
              "log": [
                {
                  id:uuid(),
                  prompt:"text3(user)",
                  response:"text1(bot)",
                },
                {
                  id:uuid(),
                  prompt:"text2(user)",
                  response:"text2(bot)",
                }          
              ]
            }
        ]
        await this.sleep(1000);
        return chatData
    }

    sleep(ms) {
      return new Promise(resolve => {
        setTimeout(resolve, ms);
      });
    }
    
    async converse(chat,prompt){
      const chat_id = chat.id
      if (!chat_id){
        return await self.create_new_chat(prompt)
      }else{
        return await self.update_chat(chat_id,prompt)
      }
    }

    async create_new_chat(prompt){
      const path = "/c"
      const method = "POST"
      const url = this.base_url + path
      const data = {
        "prompt":prompt
      }
      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const res = await response.json();
      if (res.statusCode !== 200){
        return res.message
      }else{
        return res.data
      }
    }

    async update_chat(chat_id,prompt){
      const path = `/c/${chat_id}`
      const method = "PUT"
      const url = this.base_url + path
      const data = {
        "prompt":prompt
      }
      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const res = await response.json();
      if (res.statusCode !== 200){
        return res.message
      }else{
        return res.data
      }
    }

}

async function postData(url = "", data = {}) {
  // Default options are marked with *
  const url = self.base_url + path
  const method = ""
  const response = await fetch(url, {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.json();
}

let client = new APIClient();


export default client;