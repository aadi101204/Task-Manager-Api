import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

interface User {
    id: number;
    username: string;
    email: string;
}

interface Task {
    id: number;
    title: string;
    description: string;
    status: string;
    priority: string;
    due_date: string;
    assigned_user_id: number;
    project_id: number;
}

const Tasks = () => {
    const { token } = useAuth();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [projectId, setProjectId] = useState<number | null>(null);

    // Form State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [priority, setPriority] = useState('medium');
    const [assignedTo, setAssignedTo] = useState('');
    const [dueDate, setDueDate] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (token) {
            initializeData();
        }
    }, [token]);

    const initializeData = async () => {
        await fetchUsers();
        await ensureProjectAndFetchTasks();
    };

    const fetchUsers = async () => {
        try {
            const res = await axios.get('http://localhost:8000/auth/users', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(res.data);
        } catch (err) {
            console.error("Failed to fetch users", err);
        }
    };

    const ensureProjectAndFetchTasks = async () => {
        try {
            // 1. Check for existing projects
            const projectsRes = await axios.get('http://localhost:8000/projects/', {
                headers: { Authorization: `Bearer ${token}` }
            });

            let defaultProjectId;

            if (projectsRes.data.length > 0) {
                defaultProjectId = projectsRes.data[0].id;
            } else {
                // 2. Create default project if none exist
                console.log("No projects found. Creating default 'My Tasks' project.");
                const createRes = await axios.post('http://localhost:8000/projects/', {
                    title: "My Tasks",
                    description: "Default personal project"
                }, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                defaultProjectId = createRes.data.id;
            }

            setProjectId(defaultProjectId);

            // 3. Fetch tasks for this project
            const tasksRes = await axios.get(`http://localhost:8000/tasks/?project_id=${defaultProjectId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTasks(tasksRes.data);

        } catch (err) {
            console.error("Failed to initialize project/tasks", err);
            setError("Failed to load project data. Please try refreshing.");
        }
    };

    const handleCreateTask = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (!assignedTo) {
            setError("Please assign the task to a user.");
            setLoading(false);
            return;
        }

        if (!projectId) {
            setError("No project found. Please refresh the page.");
            setLoading(false);
            return;
        }

        try {
            const payload = {
                title,
                description,
                priority,
                assigned_user_id: Number(assignedTo),
                project_id: projectId, // API requires this
                due_date: dueDate ? new Date(dueDate).toISOString() : new Date().toISOString()
            };

            await axios.post('http://localhost:8000/tasks/', payload, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // Reset form
            setTitle('');
            setDescription('');
            setAssignedTo('');
            setDueDate('');

            // Refresh tasks
            const tasksRes = await axios.get(`http://localhost:8000/tasks/?project_id=${projectId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTasks(tasksRes.data);

        } catch (err) {
            console.error("Failed to create task", err);
            setError("Failed to create task. Check console.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 space-y-8">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">Task Management</h1>
                {projectId && <span className="text-sm text-gray-500">Project ID: {projectId}</span>}
            </div>

            <div className="grid gap-8 md:grid-cols-2">
                {/* Create Task Form */}
                <Card>
                    <CardHeader>
                        <CardTitle>Create New Task</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleCreateTask} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Title</label>
                                <Input
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="Task title"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Description</label>
                                <Input
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="Task description"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Priority</label>
                                <select
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    value={priority}
                                    onChange={(e) => setPriority(e.target.value)}
                                >
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Assign To</label>
                                <select
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    value={assignedTo}
                                    onChange={(e) => setAssignedTo(e.target.value)}
                                    required
                                >
                                    <option value="">Select a user...</option>
                                    {users.map(u => (
                                        <option key={u.id} value={u.id}>
                                            {u.username} ({u.email})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Due Date</label>
                                <Input
                                    type="date"
                                    value={dueDate}
                                    onChange={(e) => setDueDate(e.target.value)}
                                    required
                                />
                            </div>

                            {error && <p className="text-red-500 text-sm">{error}</p>}

                            <Button type="submit" className="w-full" disabled={loading}>
                                {loading ? 'Creating...' : 'Create Task'}
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                {/* Task List */}
                <Card>
                    <CardHeader>
                        <CardTitle>Existing Tasks</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4 max-h-[600px] overflow-y-auto">
                            {tasks.length === 0 ? (
                                <p className="text-gray-500 text-sm">No tasks found in project.</p>
                            ) : (
                                tasks.map(task => (
                                    <div key={task.id} className="p-4 border rounded-lg bg-white shadow-sm">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-semibold">{task.title}</h3>
                                                <p className="text-sm text-gray-600">{task.description}</p>
                                            </div>
                                            <span className={`px-2 py-1 text-xs rounded-full ${task.priority === 'high' ? 'bg-red-100 text-red-800' :
                                                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-green-100 text-green-800'
                                                }`}>
                                                {task.priority}
                                            </span>
                                        </div>
                                        <div className="mt-2 text-xs text-gray-500 flex justify-between">
                                            <span>Assignee: {users.find(u => u.id === task.assigned_user_id)?.username || task.assigned_user_id}</span>
                                            <span>Status: {task.status}</span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Tasks;
