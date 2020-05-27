void playList(vector<char> & A) {
    bool Tay = // YOUR CODE HERE!!
    for (int i = 1; i < A.size(); i++){
        int next = findNext(A, i, Tay);
        swap(A[next],A[i]);
        Tay = !Tay;
    }
}