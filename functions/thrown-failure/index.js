var iopipe = require('iopipe')({ clientId: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6ImF1dGgwfDU4MTA4ZWU4MDA0NDE0YWU2NzkxMzMyZCIsInVzZXJuYW1lIjoiaW9waXBlX2RlbW8iLCJpYXQiOjE0Nzc0ODAxOTcsImF1ZCI6Imh0dHBzOi8vbWV0cmljcy1hcGkuaW9waXBlLmNvbS9ldmVudC8ifQ.rqy-hDI5x_nSJaQiVUviX5YH6OhzR7HMEQG79d_OuRw" })
exports.handle = iopipe(
  function (event, context) {
    var lineNumber = (Math.random()*100).toPrecision(2)
    // use lineNumber to determine what kind of error
    if(lineNumber > 50) {
      throw(new TypeError("This is a thrown error of TypeError!", "someFile.js", parseInt(lineNumber)))
    }

    throw(new Error("This is a thrown error of Error!"))
    context.succeed('This is my serverless function!')
  }
)