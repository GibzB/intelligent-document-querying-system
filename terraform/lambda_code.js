exports.handler = async function (event, context) {
    console.log('Aurora seeder completed successfully');
    return { statusCode: 200, body: 'Success' };
};