FROM node:14

ARG BUILD_TYPE
ENV NODE_ENV=${BUILD_TYPE:+dev}

WORKDIR /app
COPY package*.json ./

RUN if [ -e "node_modules" ]; then \
      echo "Using cached node_modules from volume"; \
    else \
      npm install; \
    fi

COPY . . 

CMD ["npm","start"]


# RUN if [ "${BUILD_TYPE}" = "prod" ]; then \
#         npm run build && \
#         npm install -g serve;\
#     fi
# CMD ['sh', '-c', "\
#     if [ \"${NODE_ENV}" = \"\prod\" ]; then \
#         serve -s build; \
#     else \
#         npm start; \
#     fi"]
    
