

const Docs = () => {
    return (
        <div className="h-screen w-full">
            <iframe
                src="http://localhost:8000/docs"
                title="API Documentation"
                className="w-full h-full border-none"
            />
        </div>
    );
};

export default Docs;
