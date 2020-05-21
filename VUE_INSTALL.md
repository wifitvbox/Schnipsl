Vorhandene Packete aktualisieren

npm install -g npm

npm install -g @vue/cli
npm install -g @vue/cli-init

vue init pwa klobs_1 (oder vue create klobs_1)
cd router-project
 das wohl anscheinend nicht ?: npm install
vue add vuetify router

? Use history mode for router? (Requires proper server setup for index fallback 
in production) No


npm install vue-i18n

Installieren in eine Webpack-Umgebung:

npm install vuetify

npm install sass sass-loader fibers deepmerge -D


Wenn man Webpack verwndet, kommt diese ganze Arie noch dazu:

https://vuetifyjs.com/en/getting-started/quick-start/#webpack-install




Font installation
Vuetify uses Google's Roboto font and Material Design Icons. The simplest way to install these are to include their CDN's in your main index.html.

<link href="https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@mdi/font@4.x/css/materialdesignicons.min.css" rel="stylesheet">



npm run dev


When es  dann aber zu Fehlermeldungen kommt (Error from chokidar ... ENOSPC), hilft:

https://github.com/guard/listen/wiki/Increasing-the-amount-of-inotify-watchers#the-technical-details
