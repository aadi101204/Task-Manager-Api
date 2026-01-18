import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Button } from '../components/ui/button';

const Dashboard = () => {
    const { token, logout } = useAuth();
    const [stats, setStats] = useState<{ name: string, count: number }[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // Fetch tasks to generate some stats
                // In a real app, this would be a dedicated stats endpoint
                const response = await axios.get('http://localhost:8000/tasks/', {
                    headers: { Authorization: `Bearer ${token}` }
                });

                const tasks = response.data;
                const completed = tasks.filter((t: any) => t.is_completed).length;
                const pending = tasks.length - completed;

                setStats([
                    { name: 'Completed', count: completed },
                    { name: 'Pending', count: pending },
                    { name: 'Total', count: tasks.length }
                ]);
            } catch (error) {
                console.error("Failed to fetch stats", error);
            } finally {
                setLoading(false);
            }
        };

        if (token) {
            fetchStats();
        }
    }, [token]);

    return (
        <div className="p-8 space-y-8">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <div className="space-x-4">
                    <Button variant="outline" onClick={() => window.location.href = '/tasks'}>Manage Tasks</Button>
                    <Button variant="destructive" onClick={logout}>Logout</Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{loading ? '...' : stats.find(s => s.name === 'Total')?.count || 0}</div>
                    </CardContent>
                </Card>
                {/* Add more cards as needed */}
            </div>

            <Card className="col-span-4">
                <CardHeader>
                    <CardTitle>Task Overview</CardTitle>
                </CardHeader>
                <CardContent className="pl-2">
                    <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={stats}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="count" fill="#adfa1d" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        </div>
    );
};

export default Dashboard;
