import { v4 as uuid } from "uuid";

class APIClient {
    constructor() {  
        if (!APIClient.instance) {
            APIClient.instance = this;
            this.base_url = "";
        }
    }


    async fetchChats() {
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
        console.log("handle converse")
        const res = {
            id:chat.id === null ? uuid():chat.id,
            title: `title_${uuid()}`,
            data: {
                id:uuid(),
                prompt:prompt,
                response: "response bot chat"
            }
        }
        //api
        await this.sleep(2000);
        return res;
    }
}


let client = new APIClient();


export default client;