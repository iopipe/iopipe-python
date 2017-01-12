var iopipe = require('iopipe')({ clientId: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6ImF1dGgwfDU4MTA4ZWU4MDA0NDE0YWU2NzkxMzMyZCIsInVzZXJuYW1lIjoiaW9waXBlX2RlbW8iLCJpYXQiOjE0Nzc0ODAxOTcsImF1ZCI6Imh0dHBzOi8vbWV0cmljcy1hcGkuaW9waXBlLmNvbS9ldmVudC8ifQ.rqy-hDI5x_nSJaQiVUviX5YH6OhzR7HMEQG79d_OuRw" })
exports.handle = iopipe(
  function (event, context) {
    iopipe.log('custom-key', 22)
    iopipe.log('another-custom-key', 'another value')  
    context.succeed('This is my serverless function with custom events!')
  }
)
