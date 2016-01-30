module.exports = function (config) {
  config.set({

    basePath: 'web/',

    files: [
      'bower_components/angular/angular.js',
      'bower_components/angular-animate/angular-animate.js',
      'bower_components/angular-aria/angular-aria.js',
      'bower_components/angular-messages/angular-messages.js',
      'bower_components/angular-mocks/angular-mocks.js',
      'bower_components/angular-material/angular-material.js',

      'src/**/*.js',

      'test/unit/**/*.js'
    ],

    logLevel: config.LOG_ERROR,
    port: 9876,
    reporters: ['progress', 'coverage'],

    preprocessors: {
      'src/**/*.js': ['coverage']
    },
    colors: true,

    autoWatch : false,
    singleRun : true,

    // For TDD mode
    //autoWatch : true,
    //singleRun : false,

    frameworks: ['jasmine'],
    browsers: ['PhantomJS'],

    plugins: [
      'karma-jasmine',
      'karma-coverage',
      'karma-phantomjs-launcher',
    ],

    coverageReporter: {
      type : 'html',
      dir : 'coverage/'
    }
  });
};