export function KillSwitchPreview() {
    return (
        <div className="border border-danger bg-dangerBg p-6 rounded-md shadow-sm">
            <h3 className="text-danger font-semibold text-lg flex items-center">
                <span className="mr-2">❌</span> DO NOT BUILD
            </h3>
            <p className="text-sm text-danger mt-2 font-medium">
                Users tolerate this pain and do not pay to solve it.
            </p>
        </div>
    );
}
