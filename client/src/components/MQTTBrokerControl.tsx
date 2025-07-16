import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useAuth } from '../contexts/AuthContext';

interface MQTTBroker {
  broker_id: number;
  broker_name: string;
  broker_host: string;
  broker_port: number;
  username?: string;
  is_active: boolean;
  connected: boolean;
  last_connected: string | null;
  last_message: string | null;
}

interface MQTTBrokerControlProps {
  className?: string;
}

interface EditingBroker {
  broker_id: number;
  broker_name: string;
  broker_host: string;
  broker_port: number;
  username: string;
  password: string;
}

const MQTTBrokerControl: React.FC<MQTTBrokerControlProps> = ({ className }) => {
  const [brokers, setBrokers] = useState<MQTTBroker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toggleLoading, setToggleLoading] = useState<{ [key: number]: boolean }>({});
  const [editingBroker, setEditingBroker] = useState<EditingBroker | null>(null);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newBroker, setNewBroker] = useState<Omit<EditingBroker, 'broker_id'>>({
    broker_name: '',
    broker_host: '',
    broker_port: 1883,
    username: '',
    password: ''
  });
  
  const { user, isAuthenticated } = useAuth();

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="bg-white dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-slate-950 dark:text-slate-50 mb-2">Authentication Required</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            Please log in to view and manage MQTT brokers.
          </p>
          <button
            onClick={() => window.location.href = '/login'}
            className="inline-flex items-center justify-center whitespace-nowrap text-sm font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 dark:ring-offset-slate-950 dark:focus-visible:ring-slate-300 bg-slate-900 text-slate-50 hover:bg-slate-900/90 dark:bg-slate-50 dark:text-slate-900 dark:hover:bg-slate-50/90 h-9 rounded-md px-3"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  const fetchBrokers = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setError('Please log in to view MQTT brokers');
        setLoading(false);
        return;
      }

      const response = await fetch('/api/mqtt-brokers/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          setError('Authentication failed. Please login again.');
          setLoading(false);
          return;
        }
        
        // Check if response is HTML (when API endpoint doesn't exist)
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
          setError('API endpoint not found. Please check if the backend server is running.');
          setLoading(false);
          return;
        }
        
        throw new Error('Failed to fetch brokers');
      }

      const data = await response.json();
      setBrokers(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching brokers:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch brokers');
    } finally {
      setLoading(false);
    }
  };

  const toggleBroker = async (brokerId: number, currentlyConnected: boolean) => {
    setToggleLoading(prev => ({ ...prev, [brokerId]: true }));
    
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const action = currentlyConnected ? 'disconnect' : 'connect';
      const response = await fetch(`/api/mqtt-brokers/brokers/${brokerId}/control`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });

      if (!response.ok) {
        throw new Error(`Failed to ${action} broker`);
      }

      // Refresh broker status
      await fetchBrokers();
    } catch (err) {
      console.error('Error toggling broker:', err);
      setError(err instanceof Error ? err.message : 'Failed to toggle broker');
    } finally {
      setToggleLoading(prev => ({ ...prev, [brokerId]: false }));
    }
  };

  const updateBroker = async (brokerData: EditingBroker) => {
    setUpdateLoading(true);
    
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`/api/mqtt-brokers/brokers/${brokerData.broker_id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          broker_name: brokerData.broker_name,
          broker_host: brokerData.broker_host,
          broker_port: brokerData.broker_port,
          username: brokerData.username,
          password: brokerData.password,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update broker');
      }

      await fetchBrokers();
      setEditingBroker(null);
      setError(null);
    } catch (err) {
      console.error('Error updating broker:', err);
      setError(err instanceof Error ? err.message : 'Failed to update broker');
    } finally {
      setUpdateLoading(false);
    }
  };

  const addBroker = async (brokerData: Omit<EditingBroker, 'broker_id'>) => {
    setUpdateLoading(true);
    
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch('/api/mqtt-brokers/brokers', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(brokerData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add broker');
      }

      await fetchBrokers();
      setShowAddForm(false);
      setNewBroker({
        broker_name: '',
        broker_host: '',
        broker_port: 1883,
        username: '',
        password: ''
      });
      setError(null);
    } catch (err) {
      console.error('Error adding broker:', err);
      setError(err instanceof Error ? err.message : 'Failed to add broker');
    } finally {
      setUpdateLoading(false);
    }
  };

  const deleteBroker = async (brokerId: number) => {
    if (!confirm('Are you sure you want to delete this broker?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`/api/mqtt-brokers/brokers/${brokerId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete broker');
      }

      await fetchBrokers();
      setError(null);
    } catch (err) {
      console.error('Error deleting broker:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete broker');
    }
  };

  const startEdit = (broker: MQTTBroker) => {
    setEditingBroker({
      broker_id: broker.broker_id,
      broker_name: broker.broker_name,
      broker_host: broker.broker_host,
      broker_port: broker.broker_port,
      username: broker.username || '',
      password: ''
    });
  };

  const cancelEdit = () => {
    setEditingBroker(null);
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingBroker) {
      updateBroker(editingBroker);
    }
  };

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    addBroker(newBroker);
  };

  useEffect(() => {
    if (user) {
      fetchBrokers();
      
      // Refresh broker status every 5 seconds
      const interval = setInterval(fetchBrokers, 5000);
      
      return () => clearInterval(interval);
    }
  }, [user]);

  // Show authentication error if user is not logged in
  if (!user) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="text-red-500 text-center">
          <p className="mb-2">Please login to access MQTT broker controls</p>
          <Button onClick={() => window.location.href = '/login'} variant="outline" size="sm">
            Go to Login
          </Button>
        </div>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="text-red-500 text-center">
          <p className="mb-2">Error: {error}</p>
          <Button onClick={fetchBrokers} variant="outline" size="sm">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">MQTT Brokers</h3>
        <div className="flex space-x-2">
          <Button onClick={() => setShowAddForm(true)} variant="default" size="sm">
            Add Broker
          </Button>
          <Button onClick={fetchBrokers} variant="outline" size="sm">
            Refresh
          </Button>
        </div>
      </div>

      {/* Add Broker Form */}
      {showAddForm && (
        <Card className="p-4 mb-4 border-2 border-dashed border-gray-300">
          <h4 className="font-semibold mb-3">Add New MQTT Broker</h4>
          <form onSubmit={handleAddSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Input
                placeholder="Broker Name"
                value={newBroker.broker_name}
                onChange={(e) => setNewBroker({...newBroker, broker_name: e.target.value})}
                required
              />
              <Input
                placeholder="Broker Host"
                value={newBroker.broker_host}
                onChange={(e) => setNewBroker({...newBroker, broker_host: e.target.value})}
                required
              />
              <Input
                type="number"
                placeholder="Port"
                value={newBroker.broker_port}
                onChange={(e) => setNewBroker({...newBroker, broker_port: parseInt(e.target.value) || 1883})}
                min="1"
                max="65535"
                required
              />
              <Input
                placeholder="Username (optional)"
                value={newBroker.username}
                onChange={(e) => setNewBroker({...newBroker, username: e.target.value})}
              />
              <Input
                type="password"
                placeholder="Password (optional)"
                value={newBroker.password}
                onChange={(e) => setNewBroker({...newBroker, password: e.target.value})}
              />
            </div>
            <div className="flex space-x-2">
              <Button type="submit" disabled={updateLoading} size="sm">
                {updateLoading ? 'Adding...' : 'Add Broker'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}
      
      {brokers.length === 0 ? (
        <p className="text-gray-500 text-center py-4">
          No MQTT brokers configured. Add your first broker to get started.
        </p>
      ) : (
        <div className="space-y-3">
          {brokers.map((broker) => (
            <div key={broker.broker_id}>
              {editingBroker?.broker_id === broker.broker_id ? (
                // Edit Form
                <Card className="p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700">
                  <form onSubmit={handleEditSubmit} className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        placeholder="Broker Name"
                        value={editingBroker.broker_name}
                        onChange={(e) => setEditingBroker({...editingBroker, broker_name: e.target.value})}
                        required
                      />
                      <Input
                        placeholder="Broker Host"
                        value={editingBroker.broker_host}
                        onChange={(e) => setEditingBroker({...editingBroker, broker_host: e.target.value})}
                        required
                      />
                      <Input
                        type="number"
                        placeholder="Port"
                        value={editingBroker.broker_port}
                        onChange={(e) => setEditingBroker({...editingBroker, broker_port: parseInt(e.target.value) || 1883})}
                        min="1"
                        max="65535"
                        required
                      />
                      <Input
                        placeholder="Username (optional)"
                        value={editingBroker.username}
                        onChange={(e) => setEditingBroker({...editingBroker, username: e.target.value})}
                      />
                      <Input
                        type="password"
                        placeholder="Password (leave empty to keep current)"
                        value={editingBroker.password}
                        onChange={(e) => setEditingBroker({...editingBroker, password: e.target.value})}
                      />
                    </div>
                    <div className="flex space-x-2">
                      <Button type="submit" disabled={updateLoading} size="sm">
                        {updateLoading ? 'Saving...' : 'Save Changes'}
                      </Button>
                      <Button type="button" variant="outline" size="sm" onClick={cancelEdit}>
                        Cancel
                      </Button>
                    </div>
                  </form>
                </Card>
              ) : (
                // Display Mode
                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          broker.connected ? 'bg-green-500' : 'bg-red-500'
                        }`}
                      />
                      <span className="font-medium">{broker.broker_name}</span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {broker.broker_host}:{broker.broker_port}
                      {broker.username && <span className="ml-2">({broker.username})</span>}
                    </div>
                    {broker.last_connected && (
                      <div className="text-xs text-gray-500">
                        Last connected: {new Date(broker.last_connected).toLocaleString()}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">
                      {broker.connected ? 'Connected' : 'Disconnected'}
                    </span>
                    
                    {/* Edit Button - only when disconnected */}
                    {!broker.connected && (
                      <Button
                        onClick={() => startEdit(broker)}
                        variant="outline"
                        size="sm"
                        className="min-w-[60px]"
                      >
                        Edit
                      </Button>
                    )}
                    
                    {/* Delete Button - only when disconnected */}
                    {!broker.connected && (
                      <Button
                        onClick={() => deleteBroker(broker.broker_id)}
                        variant="outline"
                        size="sm"
                        className="min-w-[60px] text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        Delete
                      </Button>
                    )}
                    
                    {/* Connect/Disconnect Button */}
                    <Button
                      onClick={() => toggleBroker(broker.broker_id, broker.connected)}
                      disabled={toggleLoading[broker.broker_id] || !broker.is_active}
                      variant={broker.connected ? "secondary" : "default"}
                      size="sm"
                      className={`min-w-[80px] ${
                        broker.connected 
                          ? 'bg-red-500 hover:bg-red-600 text-white' 
                          : 'bg-green-500 hover:bg-green-600 text-white'
                      }`}
                    >
                      {toggleLoading[broker.broker_id] ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : (
                        broker.connected ? 'Disconnect' : 'Connect'
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

export default MQTTBrokerControl;
