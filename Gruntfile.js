"use strict";

module.exports = function(grunt) {

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-angular-templates');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-usemin');
  grunt.loadNpmTasks('grunt-htmlrefs');
  grunt.loadNpmTasks('grunt-contrib-htmlmin');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  // Default task(s).
  grunt.registerTask('build', [
    'htmlrefs',
    'useminPrepare',
    'ngtemplates:angular',
    'concat:generated',
    'cssmin:generated',
    'uglify:generated',
    'usemin',
    'htmlmin:app'
  ]);

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    htmlrefs: {
      dist: {
        src: 'web/app.html',
        dest: 'build/web/usemin/app.html'
      }
    },
    useminPrepare: {
      html: 'build/web/usemin/app.html',
      options: {
        root: 'web/',
        staging: 'build/web/usemin',
        dest: 'build/web/dist'
      }
    },
    ngtemplates:  {
      angular: {
        cwd: 'web',
        src: 'src/**/*.html',
        dest: 'build/web/angular/templates.js',
        options:  {
          usemin: 'assets/app.js',
          module: 'tichu-tournament',
          standalone: false,
          htmlmin: {
            collapseBooleanAttributes:      true,
            collapseWhitespace:             true,
            removeAttributeQuotes:          true,
            removeComments:                 true,
            removeEmptyAttributes:          true,
            removeRedundantAttributes:      true,
            removeScriptTypeAttributes:     true,
            removeStyleLinkTypeAttributes:  true
          }
        }
      }
    },
    uglify: {
      options: {
        report: 'min',
        mangle: false
      }
    },
    usemin: {
      html: 'build/web/usemin/app.html'
    },
    htmlmin: {
      app: {
        files: {
          'build/web/dist/app.html': 'build/web/usemin/app.html'
        },
        options: {
          collapseBooleanAttributes:      true,
          collapseWhitespace:             true,
          removeAttributeQuotes:          true,
          removeComments:                 true,
          removeEmptyAttributes:          true,
          removeRedundantAttributes:      true,
          removeScriptTypeAttributes:     true,
          removeStyleLinkTypeAttributes:  true
        }
      }
    }
  });

};