/* ------------------------------------------------------------
name: "guitar_grit"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn GuitarGrit -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __GuitarGrit_H__
#define  __GuitarGrit_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS GuitarGrit
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

static float GuitarGrit_faustpower2_f(float value) {
	return value * value;
}

class GuitarGrit : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	float fConst8;
	float fConst10;
	float fConst12;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec4[2];
	float fConst13;
	float fConst14;
	float fConst15;
	int iRec5[2];
	FAUSTFLOAT fHslider0;
	float fConst16;
	float fRec6[2];
	FAUSTFLOAT fHslider1;
	int IOTA0;
	float fVec1[8192];
	FAUSTFLOAT fHslider2;
	float fRec3[3];
	FAUSTFLOAT fHslider3;
	float fRec2[3];
	float fConst17;
	float fRec1[3];
	float fVec2[2];
	float fConst19;
	float fConst21;
	float fConst22;
	float fRec0[2];
	FAUSTFLOAT fHslider4;
	
 public:
	GuitarGrit() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn GuitarGrit -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "guitar_grit.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "guitar_grit");
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
		float fConst1 = std::tan(17278.76f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / GuitarGrit_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 1.4142135f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		float fConst7 = std::tan(9110.619f / fConst0);
		fConst8 = 2.0f * (1.0f - 1.0f / GuitarGrit_faustpower2_f(fConst7));
		float fConst9 = 1.0f / fConst7;
		fConst10 = (fConst9 + -0.625f) / fConst7 + 1.0f;
		float fConst11 = (fConst9 + 0.625f) / fConst7 + 1.0f;
		fConst12 = 1.0f / fConst11;
		fConst13 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst14 = 1.0f / fConst13;
		fConst15 = 1.0f / std::max<float>(1.0f, 0.009f * fConst0);
		fConst16 = 3.1415927f / fConst0;
		fConst17 = 3.0f / (fConst7 * fConst11);
		float fConst18 = std::tan(235.61945f / fConst0);
		fConst19 = 1.0f / (fConst18 * fConst5);
		float fConst20 = 1.0f / fConst18;
		fConst21 = 1.0f - fConst20;
		fConst22 = 1.0f / (fConst20 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(7e+03f);
		fHslider1 = FAUSTFLOAT(0.996f);
		fHslider2 = FAUSTFLOAT(1.1e+02f);
		fHslider3 = FAUSTFLOAT(0.75f);
		fHslider4 = FAUSTFLOAT(0.65f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec4[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec5[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec6[l3] = 0.0f;
		}
		IOTA0 = 0;
		for (int l4 = 0; l4 < 8192; l4 = l4 + 1) {
			fVec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec2[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec1[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec2[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec0[l9] = 0.0f;
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
	
	virtual GuitarGrit* clone() {
		return new GuitarGrit();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("guitar_grit");
		ui_interface->addHorizontalSlider("damp", &fHslider0, FAUSTFLOAT(7e+03f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(1e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("drive", &fHslider3, FAUSTFLOAT(0.75f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sustain", &fHslider1, FAUSTFLOAT(0.996f), FAUSTFLOAT(0.98f), FAUSTFLOAT(0.999f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 1.0f / std::tan(fConst16 * std::max<float>(0.1f, fSlow0) * float(fHslider0));
		float fSlow2 = 1.0f - fSlow1;
		float fSlow3 = 1.0f / (fSlow1 + 1.0f);
		float fSlow4 = float(fHslider1);
		float fSlow5 = fConst0 / float(fHslider2);
		float fSlow6 = fSlow5 + -2.0f;
		int iSlow7 = int(fSlow6);
		int iSlow8 = std::min<int>(4097, std::max<int>(0, iSlow7 + 1));
		float fSlow9 = std::floor(fSlow6);
		float fSlow10 = fSlow5 + (-2.0f - fSlow9);
		int iSlow11 = std::min<int>(4097, std::max<int>(0, iSlow7));
		float fSlow12 = fSlow9 + (3.0f - fSlow5);
		float fSlow13 = 11.0f * float(fHslider3) + 1.5f;
		float fSlow14 = 0.16408f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec4[0] = (iRec4[1] + (iRec4[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec4[0]);
			iRec5[0] = 1103515245 * iRec5[1] + 12345;
			fRec6[0] = -(fSlow3 * (fSlow2 * fRec6[1] - (fRec3[1] + fRec3[2])));
			float fTemp1 = fSlow4 * fRec6[0] + 4.656613e-10f * float(iRec5[0]) * std::max<float>(0.0f, std::min<float>(fConst14 * fTemp0, fConst15 * (fConst13 - fTemp0) + 1.0f));
			fVec1[IOTA0 & 8191] = fTemp1;
			fRec3[0] = fSlow12 * fVec1[(IOTA0 - iSlow11) & 8191] + fSlow10 * fVec1[(IOTA0 - iSlow8) & 8191];
			float fTemp2 = tanhf(fSlow13 * fRec3[0]);
			fRec2[0] = fTemp2 - fConst12 * (fConst10 * fRec2[2] + fConst8 * fRec2[1]);
			fRec1[0] = fTemp2 + fConst17 * (fRec2[0] - fRec2[2]) - fConst6 * (fConst4 * fRec1[2] + fConst2 * fRec1[1]);
			float fTemp3 = fRec1[2] + fRec1[0] + 2.0f * fRec1[1];
			fVec2[0] = fTemp3;
			fRec0[0] = -(fConst22 * (fConst21 * fRec0[1] - fConst19 * (fTemp3 - fVec2[1])));
			float fTemp4 = fSlow14 * fRec0[0];
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			fVec0[1] = fVec0[0];
			iRec4[1] = iRec4[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
			IOTA0 = IOTA0 + 1;
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fVec2[1] = fVec2[0];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
