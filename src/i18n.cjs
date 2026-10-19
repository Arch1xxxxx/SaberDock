const messages = require('./messages.json');
exports.tr = message => {
  if (process.env.SABERDOCK_LANGUAGE === 'zh-Hans') return message;
  if (!Object.hasOwn(messages, message)) throw new Error(`Missing translation: ${message}`);
  return messages[message];
};
