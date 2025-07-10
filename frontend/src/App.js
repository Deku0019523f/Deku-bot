import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [botConfig, setBotConfig] = useState({
    name: '',
    description: '',
    features: [],
    commands: ['start', 'help'],
    has_inline_buttons: false,
    has_webhook: false,
    has_database: false,
    token_var_name: 'BOT_TOKEN'
  });
  const [generatedCode, setGeneratedCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('builder');
  const [myBots, setMyBots] = useState([]);
  const [showInstructions, setShowInstructions] = useState(false);

  // Charger les templates au démarrage
  useEffect(() => {
    loadTemplates();
    loadMyBots();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/api/templates`);
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error('Erreur lors du chargement des templates:', error);
    }
  };

  const loadMyBots = async () => {
    try {
      const response = await fetch(`${API_URL}/api/bots`);
      const data = await response.json();
      setMyBots(data);
    } catch (error) {
      console.error('Erreur lors du chargement des bots:', error);
    }
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setBotConfig(prev => ({
        ...prev,
        features: template.features,
        has_inline_buttons: template.features.includes('buttons'),
        commands: template.features.includes('commands') ? ['start', 'help', 'info', 'ping'] : ['start', 'help']
      }));
    }
  };

  const handleConfigChange = (field, value) => {
    setBotConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCommandAdd = () => {
    const newCommand = prompt('Nom de la nouvelle commande (sans /):', '');
    if (newCommand && !botConfig.commands.includes(newCommand)) {
      setBotConfig(prev => ({
        ...prev,
        commands: [...prev.commands, newCommand]
      }));
    }
  };

  const handleCommandRemove = (command) => {
    if (command === 'start' || command === 'help') return;
    setBotConfig(prev => ({
      ...prev,
      commands: prev.commands.filter(cmd => cmd !== command)
    }));
  };

  const generateBot = async () => {
    if (!botConfig.name || !botConfig.description) {
      alert('Veuillez remplir le nom et la description du bot');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(botConfig)
      });

      const data = await response.json();
      if (data.success) {
        setGeneratedCode(data.code);
        setActiveTab('code');
        setShowInstructions(true);
        loadMyBots(); // Recharger la liste des bots
      } else {
        alert('Erreur lors de la génération du code');
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de la génération du code');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Code copié dans le presse-papiers !');
    } catch (error) {
      console.error('Erreur lors de la copie:', error);
    }
  };

  const deleteBot = async (botId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce bot ?')) {
      try {
        await fetch(`${API_URL}/api/bots/${botId}`, {
          method: 'DELETE'
        });
        loadMyBots();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const viewBotCode = async (botId) => {
    try {
      const response = await fetch(`${API_URL}/api/bots/${botId}`);
      const bot = await response.json();
      setGeneratedCode(bot.code);
      setActiveTab('code');
    } catch (error) {
      console.error('Erreur lors du chargement du bot:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">🤖</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">TeleBot Builder</h1>
                <p className="text-gray-600">Créez votre bot Telegram en quelques clics</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                ✨ Générateur AI
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('builder')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'builder'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              🛠️ Générateur
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'code'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📝 Code Généré
            </button>
            <button
              onClick={() => setActiveTab('mybots')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'mybots'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              💾 Mes Bots ({myBots.length})
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Tab: Builder */}
        {activeTab === 'builder' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Configuration du bot */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  🎯 Configuration du Bot
                </h2>

                {/* Informations de base */}
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom du Bot *
                    </label>
                    <input
                      type="text"
                      value={botConfig.name}
                      onChange={(e) => handleConfigChange('name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="MonSuperBot"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description *
                    </label>
                    <textarea
                      value={botConfig.description}
                      onChange={(e) => handleConfigChange('description', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows="3"
                      placeholder="Ce bot fait des choses incroyables..."
                    />
                  </div>
                </div>

                {/* Templates */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    🎨 Templates Disponibles
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {templates.map((template) => (
                      <div
                        key={template.id}
                        onClick={() => handleTemplateSelect(template.id)}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          selectedTemplate === template.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <h4 className="font-medium text-gray-900">{template.name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {template.features.map((feature) => (
                            <span
                              key={feature}
                              className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Commandes */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    ⚡ Commandes
                  </h3>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {botConfig.commands.map((command) => (
                      <div
                        key={command}
                        className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
                          command === 'start' || command === 'help'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        <span>/{command}</span>
                        {command !== 'start' && command !== 'help' && (
                          <button
                            onClick={() => handleCommandRemove(command)}
                            className="text-red-500 hover:text-red-700"
                          >
                            ✕
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={handleCommandAdd}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    ➕ Ajouter Commande
                  </button>
                </div>

                {/* Options avancées */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    🔧 Options Avancées
                  </h3>
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={botConfig.has_inline_buttons}
                        onChange={(e) => handleConfigChange('has_inline_buttons', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        Boutons interactifs (inline keyboards)
                      </span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={botConfig.has_webhook}
                        onChange={(e) => handleConfigChange('has_webhook', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        Support des webhooks
                      </span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={botConfig.has_database}
                        onChange={(e) => handleConfigChange('has_database', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        Intégration base de données
                      </span>
                    </label>
                  </div>
                </div>

                {/* Bouton de génération */}
                <button
                  onClick={generateBot}
                  disabled={loading || !botConfig.name || !botConfig.description}
                  className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
                    loading || !botConfig.name || !botConfig.description
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {loading ? '⏳ Génération en cours...' : '🚀 Générer le Bot'}
                </button>
              </div>
            </div>

            {/* Aperçu */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-sm p-6 sticky top-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  👀 Aperçu
                </h3>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-700">Nom:</h4>
                    <p className="text-gray-600">{botConfig.name || 'Non défini'}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-700">Description:</h4>
                    <p className="text-gray-600">{botConfig.description || 'Non définie'}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-700">Commandes:</h4>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {botConfig.commands.map((cmd) => (
                        <span key={cmd} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          /{cmd}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-700">Fonctionnalités:</h4>
                    <div className="space-y-1 mt-1">
                      <div className="flex items-center text-sm">
                        <span className={botConfig.has_inline_buttons ? 'text-green-600' : 'text-gray-400'}>
                          {botConfig.has_inline_buttons ? '✅' : '❌'}
                        </span>
                        <span className="ml-2">Boutons interactifs</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className={botConfig.has_webhook ? 'text-green-600' : 'text-gray-400'}>
                          {botConfig.has_webhook ? '✅' : '❌'}
                        </span>
                        <span className="ml-2">Webhooks</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className={botConfig.has_database ? 'text-green-600' : 'text-gray-400'}>
                          {botConfig.has_database ? '✅' : '❌'}
                        </span>
                        <span className="ml-2">Base de données</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab: Code */}
        {activeTab === 'code' && (
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900">
                    📝 Code Généré
                  </h2>
                  {generatedCode && (
                    <button
                      onClick={() => copyToClipboard(generatedCode)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      📋 Copier le Code
                    </button>
                  )}
                </div>
              </div>
              <div className="p-6">
                {generatedCode ? (
                  <div className="space-y-6">
                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono">
                      <code>{generatedCode}</code>
                    </pre>
                    
                    {showInstructions && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-blue-900 mb-4">
                          🚀 Instructions d'installation
                        </h3>
                        <div className="space-y-3">
                          <div>
                            <h4 className="font-medium text-blue-800">1. Créer un bot Telegram</h4>
                            <p className="text-blue-700 text-sm">
                              Envoyez un message à @BotFather sur Telegram et suivez les instructions pour créer votre bot.
                            </p>
                          </div>
                          <div>
                            <h4 className="font-medium text-blue-800">2. Installer les dépendances</h4>
                            <pre className="bg-blue-100 text-blue-900 p-2 rounded text-sm font-mono">
                              pip install python-telegram-bot python-dotenv
                            </pre>
                          </div>
                          <div>
                            <h4 className="font-medium text-blue-800">3. Configurer le token</h4>
                            <p className="text-blue-700 text-sm">
                              Créez un fichier <code className="bg-blue-100 px-1 rounded">.env</code> avec votre token :
                            </p>
                            <pre className="bg-blue-100 text-blue-900 p-2 rounded text-sm font-mono">
                              BOT_TOKEN=votre_token_ici
                            </pre>
                          </div>
                          <div>
                            <h4 className="font-medium text-blue-800">4. Lancer le bot</h4>
                            <pre className="bg-blue-100 text-blue-900 p-2 rounded text-sm font-mono">
                              python bot.py
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">📝</span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Aucun code généré
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Utilisez le générateur pour créer votre premier bot.
                    </p>
                    <button
                      onClick={() => setActiveTab('builder')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      🛠️ Aller au Générateur
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab: Mes Bots */}
        {activeTab === 'mybots' && (
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900">
                  💾 Mes Bots ({myBots.length})
                </h2>
              </div>
              <div className="p-6">
                {myBots.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {myBots.map((bot) => (
                      <div
                        key={bot.id}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="font-semibold text-gray-900">{bot.name}</h3>
                            <p className="text-sm text-gray-600 mt-1">{bot.description}</p>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => viewBotCode(bot.id)}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              👁️ Voir
                            </button>
                            <button
                              onClick={() => deleteBot(bot.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              🗑️ Supprimer
                            </button>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1 mb-3">
                          {bot.features.map((feature) => (
                            <span
                              key={feature}
                              className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                        <div className="text-xs text-gray-500">
                          Créé le {new Date(bot.created_at).toLocaleDateString('fr-FR')}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">🤖</span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Aucun bot créé
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Créez votre premier bot avec le générateur.
                    </p>
                    <button
                      onClick={() => setActiveTab('builder')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                    >
                      🛠️ Créer un Bot
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;