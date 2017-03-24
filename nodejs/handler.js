var iopipe = require('iopipe')({ clientId: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6ImF1dGgwfDU4MTA4ZWU4MDA0NDE0YWU2NzkxMzMyZCIsInVzZXJuYW1lIjoiaW9waXBlX2RlbW8iLCJpYXQiOjE0Nzc0ODAxOTcsImF1ZCI6Imh0dHBzOi8vbWV0cmljcy1hcGkuaW9waXBlLmNvbS9ldmVudC8ifQ.rqy-hDI5x_nSJaQiVUviX5YH6OhzR7HMEQG79d_OuRw" })

exports.simpleSuccess = iopipe(
  function (event, context) {
    context.succeed('This is my serverless function!')
  }
);

exports.simpleFailure = iopipe(
  function (event, context) {
    context.fail('This is my failing serverless function!');
  }
);

exports.randomSuccessError = iopipe(
  function (event, context) {
    const shouldError = Math.random() < 0.5;
    return shouldError ? context.fail('I decided to fail this time.') : context.succeed('I decided to succeed this time.');
  }
)

exports.longRunningSuccess = iopipe(
  function (event, context) {
    var duration = Math.floor(Math.random()*(2001-900+1)+900);
    setTimeout(function(){
      context.succeed('Succeeded with a set duration of ' + duration);
    }, duration);
  }
)

exports.customEvents = iopipe(
  function (event, context) {
    iopipe.log("simple-key", 42);
    iopipe.log("key with space", "a neat value");
    iopipe.log("value-too-long", 'this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length. this string is so long that it is not allowed so we cut it to a shorter length.')
    iopipe.log('undefined value', undefined);
    iopipe.log('null value', null);
    iopipe.log('random number', Math.floor(Math.random() * 10000) + 1);
    iopipe.log('long_value', 'Leverage agile frameworks to provide a robust synopsis for high level overviews. Iterative approaches to corporate strategy foster collaborative thinking to further the overall value proposition. Organically grow the holistic world view of disruptive innovation via workplace diversity and empowerment. Bring to the table win-win survival strategies to ensure proactive domination. At the end of the day, going forward, a new normal that has evolved from generation X is on the runway heading towards a streamlined cloud solution. User generated content in real-time will have multiple touchpoints for offshoring.');
    context.succeed('This is my serverless function with custom events!');
  }
)

exports.thrownFailure = iopipe(
  function (event, context) {
    var lineNumber = (Math.random()*100).toPrecision(2);
    // use lineNumber to determine what kind of error
    if(lineNumber > 50) {
      throw(new TypeError("This is a thrown error of TypeError!", "someFile.js", parseInt(lineNumber)));
    }

    throw(new Error("This is a thrown error of Error!"));
    context.succeed('This is my serverless function!');
  }
);
