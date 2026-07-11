/* ------------------------------------------------------------
name: "pluck2"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Pluck2 -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Pluck2_H__
#define  __Pluck2_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Pluck2
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Pluck2_faustpower2_f(float value) {
	return value * value;
}

class Pluck2 : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec2[2];
	float fConst2;
	float fConst3;
	float fConst4;
	int iRec3[2];
	FAUSTFLOAT fHslider1;
	float fRec4[2];
	FAUSTFLOAT fHslider2;
	int IOTA0;
	float fVec1[8192];
	FAUSTFLOAT fHslider3;
	float fRec1[3];
	float fRec0[3];
	FAUSTFLOAT fHslider4;
	
 public:
	Pluck2() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Pluck2 -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "pluck2.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "pluck2");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 1.0f / std::max<float>(1.0f, 0.01f * fConst0);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(5.2e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(6e+03f);
		fHslider2 = FAUSTFLOAT(0.985f);
		fHslider3 = FAUSTFLOAT(4.4e+02f);
		fHslider4 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec2[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec3[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		IOTA0 = 0;
		for (int l4 = 0; l4 < 8192; l4 = l4 + 1) {
			fVec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec1[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec0[l6] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Pluck2* clone() {
		return new Pluck2();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("pluck2");
		ui_interface->addHorizontalSlider("damp", &fHslider1, FAUSTFLOAT(6e+03f), FAUSTFLOAT(1e+03f), FAUSTFLOAT(1e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(4e+01f), FAUSTFLOAT(3e+03f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sustain", &fHslider2, FAUSTFLOAT(0.985f), FAUSTFLOAT(0.9f), FAUSTFLOAT(0.999f), FAUSTFLOAT(0.0001f));
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(5.2e+03f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(1e+04f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Pluck2_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 1.4142135f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fButton0);
		float fSlow7 = 1.0f / std::tan(fConst1 * float(fHslider1));
		float fSlow8 = 1.0f - fSlow7;
		float fSlow9 = 1.0f / (fSlow7 + 1.0f);
		float fSlow10 = float(fHslider2);
		float fSlow11 = fConst0 / float(fHslider3);
		float fSlow12 = fSlow11 + -2.499995f;
		int iSlow13 = int(fSlow12);
		int iSlow14 = std::min<int>(4096, std::max<int>(0, iSlow13 + 4));
		float fSlow15 = std::floor(fSlow12);
		float fSlow16 = fSlow11 + (-4.0f - fSlow15);
		float fSlow17 = fSlow11 + (-3.0f - fSlow15);
		float fSlow18 = fSlow11 + (-2.0f - fSlow15);
		float fSlow19 = fSlow11 + (-1.0f - fSlow15);
		float fSlow20 = fSlow19 * fSlow18;
		float fSlow21 = fSlow20 * fSlow17;
		float fSlow22 = 0.041666668f * fSlow21 * fSlow16;
		int iSlow23 = std::min<int>(4096, std::max<int>(0, iSlow13 + 3));
		float fSlow24 = 0.16666667f * fSlow21;
		int iSlow25 = std::min<int>(4096, std::max<int>(0, iSlow13 + 2));
		float fSlow26 = 0.25f * fSlow20;
		int iSlow27 = std::min<int>(4096, std::max<int>(0, iSlow13 + 1));
		float fSlow28 = 0.16666667f * fSlow19;
		int iSlow29 = std::min<int>(4096, std::max<int>(0, iSlow13));
		float fSlow30 = 0.041666668f * fSlow18;
		float fSlow31 = fSlow11 + (-5.0f - fSlow15);
		float fSlow32 = 0.9f * (float(fHslider4) / fSlow4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow6;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow6 <= fVec0[1]) + (fSlow6 > fVec0[1]);
			float fTemp0 = float(iRec2[0]);
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			fRec4[0] = -(fSlow9 * (fSlow8 * fRec4[1] - (fRec1[1] + fRec1[2])));
			float fTemp1 = fSlow10 * fRec4[0] + 4.656613e-10f * float(iRec3[0]) * std::max<float>(0.0f, std::min<float>(fConst3 * fTemp0, fConst4 * (fConst2 - fTemp0) + 1.0f));
			fVec1[IOTA0 & 8191] = fTemp1;
			fRec1[0] = fSlow31 * (fSlow16 * (fSlow17 * (fSlow30 * fVec1[(IOTA0 - iSlow29) & 8191] - fSlow28 * fVec1[(IOTA0 - iSlow27) & 8191]) + fSlow26 * fVec1[(IOTA0 - iSlow25) & 8191]) - fSlow24 * fVec1[(IOTA0 - iSlow23) & 8191]) + fSlow22 * fVec1[(IOTA0 - iSlow14) & 8191];
			fRec0[0] = fRec1[0] - fSlow5 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp2 = fSlow32 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp2);
			output1[i0] = FAUSTFLOAT(fTemp2);
			fVec0[1] = fVec0[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			IOTA0 = IOTA0 + 1;
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
